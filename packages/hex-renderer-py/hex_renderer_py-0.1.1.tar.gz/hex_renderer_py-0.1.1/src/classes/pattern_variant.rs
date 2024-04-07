use hex_renderer::pattern_utils::{Direction, Angle};
use interface_macros::py_type_gen;
use pyo3::{pyclass, pymethods, PyResult, exceptions::PyValueError};

use crate::angles_to_string;

#[derive(Debug, Clone)]
#[py_type_gen]
#[pyclass(name = "PatternVariant")]
///A hexpattern that can be rendered on a grid
pub struct PyPatternVariant {
    dir_str: String,
    direction: Direction,
    angle_sigs: Vec<Angle>,
    great_spell: bool,
}

#[py_type_gen]
#[pymethods]
impl PyPatternVariant {
    #[new]
    ///Creates a new PatternVariant
    /// :param direction: Starting direction (North_East, East, South_East, South_West, West, North_West)
    /// :param angle_sigs: String of angle sigs (accepted characters: [q,w,e,d,s,a])
    /// :param great_spell: Whether or not it's a great spell (Default = false)
    fn new(direction: String, angle_sigs: String, great_spell: Option<bool>) -> PyResult<Self> {
        Ok(Self {
            dir_str: direction.clone(),
            direction: (&direction[..])
                .try_into()
                .map_err(|_| PyValueError::new_err(format!("Invalid direction! {direction}")))?,
            angle_sigs: angle_sigs
                .chars()
                .map(Angle::try_from)
                .collect::<Result<Vec<_>, _>>()
                .map_err(|_| PyValueError::new_err(format!("Invalid angle_sigs! {angle_sigs}")))?,
            great_spell: great_spell.unwrap_or(false),
        })
    }

    #[getter]
    ///Gets the starting direction of the pattern 
    fn get_direction(&self) -> String {
        self.dir_str.clone()
    }
    /*#[setter]
    fn set_direction(&mut self, direction: String) -> PyResult<()> {
        let dir: Direction = (&direction[..])
            .try_into()
            .map_err(|_| PyValueError::new_err(format!("Invalid direction! {direction}")))?;

        self.dir_str = direction;
        self.direction = dir;
        Ok(())
    }*/

    #[getter]
    ///Gets the angle_sigs of the pattern
    fn get_angle_sigs(&self) -> String {
        angles_to_string(&self.angle_sigs)
    }
    /*#[setter]
    fn set_angle_sigs(&mut self, angle_sigs: String) -> PyResult<()> {
        let angles: Vec<Angle> = angle_sigs
            .chars()
            .map(Angle::try_from)
            .collect::<Result<Vec<_>, _>>()
            .map_err(|_| PyValueError::new_err(format!("Invalid angle! {angle_sigs}")))?;

        self.angle_sigs = angles;

        Ok(())
    }*/

    #[getter]
    ///Gets whether or not the pattern is a great spell
    fn get_great_spell(&self) -> bool {
        self.great_spell
    }
    /*#[setter]
    fn set_great_spell(&mut self, great_spell: bool) {
        self.great_spell = great_spell;
    }*/
}

impl From<PyPatternVariant> for hex_renderer::PatternVariant {
    fn from(value: PyPatternVariant) -> Self {
        let pattern = hex_renderer::Pattern::new(value.direction, value.angle_sigs);

        if value.great_spell {
            Self::Monocolor(pattern)
        } else {
            Self::Normal(pattern)
        }
    }
}