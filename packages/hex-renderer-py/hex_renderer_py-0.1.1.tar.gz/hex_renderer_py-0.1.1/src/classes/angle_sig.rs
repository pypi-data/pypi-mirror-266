use hex_renderer::pattern_utils::Angle;
use interface_macros::{py_type_gen, PyBridge};
use pyo3::{pyclass, PyResult, exceptions::PyTypeError, Python, pymethods};

#[py_type_gen]
#[pyclass]
#[derive(Clone)]
///Angle sigs of a pattern (ex. qqq)
pub struct AngleSig(Vec<Angle>);

#[py_type_gen]
#[pymethods]
impl AngleSig {
    #[new]
    ///Make a new angle sig
    /// :param sigs: String of sigs (ex. qqq)
    fn new(sigs: String) -> PyResult<Self> {
        let sigs = sigs.chars()
            .map(Angle::try_from)
            .collect::<Result<Vec<Angle>, _>>()
            .map_err(|_| PyTypeError::new_err("Invalid angle sig!"))?;

        Ok(Self(sigs))
    }
    /// gets the sigs as a string
    fn get_sigs(&self) -> String {
        self.0.iter().map(|angle| {
            match angle {
                Angle::Forward => 'w',
                Angle::Right => 'e',
                Angle::BackRight => 'd',
                Angle::Back => 's',
                Angle::BackLeft => 'a',
                Angle::Left => 'q',
            }
        }).collect()
    }
    fn __repr__(&self) -> String {
        format!("Angle({})", self.get_sigs())
    }
}

impl PyBridge<AngleSig> for Vec<Angle> {
    type PyOut = AngleSig;

    fn into_py(self, _py: Python) -> PyResult<Self::PyOut> {
        Ok(AngleSig(self))
    }

    fn from_py(val: AngleSig, _py: Python) -> PyResult<Self> {
        Ok(val.0)
    }
}