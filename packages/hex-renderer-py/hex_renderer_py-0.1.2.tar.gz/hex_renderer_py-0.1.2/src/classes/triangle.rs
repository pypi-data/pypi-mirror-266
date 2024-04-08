use hex_renderer::options::{Triangle, Marker};
use interface_macros::py_gen;
use pyo3::{Python, types::PyModule, PyResult};

use super::marker::PyMarker;

pub fn add_class(py: Python, m: &PyModule) -> PyResult<()> {
    let sub_m = PyModule::new(py, "Triangle")?;
    sub_m.add_class::<PyTriangleNone>()?;
    sub_m.add_class::<PyTriangleMatch>()?;
    sub_m.add_class::<PyTriangleBorderMatch>()?;
    sub_m.add_class::<PyTriangleBorderStartMatch>()?;
    
    m.add_submodule(sub_m)?;

    Ok(())
}

#[py_gen(bridge = Triangle)]
#[derive(Clone)]
///Options for drawing the triangle/arrow between color changes on the Segment Renderer
pub enum PyTriangle {
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///None, simply don't draw them
    None,
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Match the color of the line
    Match {
        ///radius is how big it is (as a percentage of segment length)
        radius: f32
    },
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Same as Triangle.Match except with an extra border around it
    BorderMatch {
        ///radius of how big the match triangle is (as a percentage of segment length)
        match_radius: f32,
        #[py_gen(bridge = PyMarker)]
        ///a Marker for the border
        border: Marker
    },
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Same as Triangle.BorderMatch except with an extra triangle right after the start point
    BorderStartMatch {
        ///radius of how big the match triangle is (as a percentage of segment length)
        match_radius: f32,
        #[py_gen(bridge = PyMarker)]
        ///a Marker for the border
        border: Marker
    }
}