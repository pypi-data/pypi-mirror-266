use std::fs;

use hex_renderer::{grids::{GridDraw, GridDrawError, SquareGrid, HexGrid}, PatternVariant, options::GridOptions};
use interface_macros::{py_type_gen, PyType, PyBridge};
use pyo3::{pyclass, PyErr, exceptions::PyValueError, FromPyObject, PyRef, pymethods, PyResult, types::PyModule, Python};

use super::{grid_options::PyGridOptions, pattern_variant::PyPatternVariant};


pub fn initialize_classes(m: &PyModule) -> PyResult<()> {
    m.add_class::<PyGrid>()?;
    m.add_class::<PyHexGrid>()?;
    m.add_class::<PySquareGrid>()?;

    Ok(())
}

#[py_type_gen]
#[pyclass(name = "Grid", subclass)]
///Grid parent class for rendering grids
/// Current grids implemented: HexGrid, SquareGrid
struct PyGrid(Box<dyn GridDraw + Send>);

fn map_draw_error(err: GridDrawError) -> PyErr {
    match err {
        GridDrawError::ImproperScale(f32) => {
            PyValueError::new_err(format!("{f32} isn't a valid scale!"))
        }
        GridDrawError::EncodeError => {
            PyValueError::new_err("Something went wrong and the grid couldn't be drawn.")
        }
    }
}

#[derive(FromPyObject)]
enum ScaleOption {
    Padding(f32),
    Options(PyGridOptions),
}

impl<'a> PyType for ScaleOption {
    fn to_string() -> String {
        format!(
            "{} | {}", 
            <f32 as PyType>::to_string(),
            <PyRef<'a, PyGridOptions> as PyType>::to_string()
        )
    }
}
#[py_type_gen]
#[pymethods]
impl PyGrid {
    ///Draws the grid and returns a PNG as an array of bytes
    /// :param scale: (HexGrid) distance between points in pixels, (SquareGrid) size of tiles
    /// :param options: The options for how to draw the patterns
    /// :param padding: Optional padding to put around the grid
    fn draw_png(
        &self,
        scale: f32,
        options: PyGridOptions,
        padding: Option<f32>,
        py: Python,
    ) -> PyResult<Vec<u8>> {
        let options: GridOptions = <GridOptions as PyBridge<PyGridOptions>>::from_py(options, py)?;
        let padding = match padding {
            Some(pad) => pad,
            None => options.get_max_radius(),
        };

        self.0
            .draw_grid_with_padding(scale, &options, padding)
            .map_err(map_draw_error)?
            .encode_png()
            .map_err(|_| PyValueError::new_err("Failed to encode into png!"))
    }

    ///Draws the grid and saves it to a file
    /// :param file_name: path to the file you want to save it as
    /// :param scale: (HexGrid) distance between points in pixels, (SquareGrid) size of tiles
    /// :param options: The options for how to draw the patterns
    /// :param padding: Optional padding to put around the grid
    fn draw_to_file(
        &self,
        file_name: &str,
        scale: f32,
        options: PyGridOptions,
        padding: Option<f32>,
        py: Python
    ) -> PyResult<()> {
        fs::write(file_name, self.draw_png(scale, options, padding, py)?)
            .map_err(|err| PyValueError::new_err(err.to_string()))
    }

    ///Gets the max scale that will fit within the given image size
    /// :param bound: x and y maximum sizes
    /// :param options: The size of padding or the GridOptions to determine it automatically
    fn get_bound_scale(&self, bound: (f32, f32), options: ScaleOption, py: Python) -> PyResult<f32> {
        let size = self.0.get_unpadded_size();

        let padding = match options {
            ScaleOption::Padding(pad) => pad,
            ScaleOption::Options(grid) => {
                let options: GridOptions = <GridOptions as PyBridge<PyGridOptions>>::from_py(grid, py)?;
                options.get_max_radius()
            }
        };

        let size = (padding * 2.0 + size.0, padding * 2.0 + size.1);

        Ok((bound.0 / size.0).min(bound.1 / size.1).max(1.0))
    }
}

#[py_type_gen]
#[pyclass(name="HexGrid", extends=PyGrid)]
///A hexagonal grid where patterns are all rendered to fit on the grid.
struct PyHexGrid;

#[py_type_gen]
#[pymethods]
impl PyHexGrid {
    #[new]
    ///Creates a hexagonal grid where patterns are all rendered to fit on the grid.
    /// :param patterns: Array of patterns to fit on to the grid
    /// :param max_width: The maximum width of the grid (in grid points) before wrapping around
    fn new(patterns: Vec<PyPatternVariant>, max_width: usize) -> PyResult<(Self, PyGrid)> {
        let patterns = patterns.into_iter().map(PatternVariant::from).collect();

        let grid = HexGrid::new(patterns, max_width)
            .map_err(|_| PyValueError::new_err("Failed to create grid!"))?;

        Ok((Self, PyGrid(Box::new(grid))))
    }
}

#[py_type_gen]
#[pyclass(name="SquareGrid", extends=PyGrid)]
///Grid of fixed sized tiles where the patterns are automatically scaled to fit within.
struct PySquareGrid;

#[py_type_gen]
#[pymethods]
impl PySquareGrid {
    #[new]
    ///Creats a grid of fixed size tiles where the patterns are automatically scaled to fit within.
    /// :param patterns: Array of patterns to fit on to the grid
    /// :param max_width: Maximum number of tiles to lay down horizontally before wrapping around
    /// :param max_scale: Maximum scale of patterns in each tile (1 is no limit)
    /// :param x_pad: amount of horizontal padding between tiles (measured in scale*x_pad pixels) 
    /// :param y_pad: amount of vertical padding between tiles (measured in scale*y_pad pixels) 
    fn new(
        patterns: Vec<PyPatternVariant>,
        max_width: usize,
        max_scale: f32,
        x_pad: f32,
        y_pad: f32,
    ) -> PyResult<(Self, PyGrid)> {
        let patterns = patterns.into_iter().map(PatternVariant::from).collect();

        let grid = SquareGrid::new(patterns, max_width, max_scale, x_pad, y_pad)
            .map_err(|_| PyValueError::new_err("Failed to create grid!"))?;

        Ok((Self, PyGrid(Box::new(grid))))
    }
}