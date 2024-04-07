use hex_renderer::{options::{GridPatternOptions, Intersections, Lines}, pattern_utils::Angle};
use interface_macros::py_gen;
use pyo3::{Python, types::PyModule, PyResult};

use super::{intersections::PyIntersections, lines::PyLines, angle_sig::AngleSig};

pub fn add_class(py: Python, m: &PyModule) -> PyResult<()> {
    let sub_m = PyModule::new(py, "GridPatternOptions")?;
    sub_m.add_class::<PyGridPatternOptionsUniform>()?;
    sub_m.add_class::<PyGridPatternOptionsChanging>()?;
    
    m.add_submodule(sub_m)?;

    Ok(())
}

#[py_gen(bridge = GridPatternOptions)]
#[derive(Clone)]
///Struct that holds the different variations of GridPatterns
pub enum PyGridPatternOptions {
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Uniform means that all patterns will be rendered in the same way
    /// (This excludes the difference with PatternVariant)
    Uniform (
        #[py_gen(name = "intersections", bridge = PyIntersections)]
        Intersections,
        #[py_gen(name = "lines", bridge = PyLines)]
        Lines
    ),
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Changes what pattern renderer to use when finding an introspect or retrospect pattern
    /// That way you can change colors/renderers for embedded patterns
    Changing {
        #[py_gen(bridge = Vec<(PyIntersections, PyLines)>)]
        ///Variations to use, starts at the first and goes up when it reaches an intro, goes down when reaching a retro
        variations: Vec<(Intersections, Lines)>,
        #[py_gen(bridge = Vec<AngleSig>)]
        ///Vec of the angle_sigs of intro patterns
        intros: Vec<Vec<Angle>>,
        #[py_gen(bridge = Vec<AngleSig>)]
        ///Vec of angle_sigs of retro patterns
        retros: Vec<Vec<Angle>>
    }
}