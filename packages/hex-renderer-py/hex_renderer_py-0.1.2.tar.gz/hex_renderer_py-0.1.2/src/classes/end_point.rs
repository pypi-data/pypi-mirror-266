use hex_renderer::options::{EndPoint, Point, Marker};
use interface_macros::py_gen;
use pyo3::{Python, types::PyModule, PyResult};

use super::{point::PyPoint, marker::PyMarker};

pub fn add_class(py: Python, m: &PyModule) -> PyResult<()> {
    let sub_m = PyModule::new(py, "EndPoint")?;
    sub_m.add_class::<PyEndPointPoint>()?;
    sub_m.add_class::<PyEndPointMatch>()?;
    sub_m.add_class::<PyEndPointBorderedMatch>()?;
    
    m.add_submodule(sub_m)?;

    Ok(())
}

#[py_gen(bridge = EndPoint)]
#[derive(Clone)]
///Specifier for how to draw the start and end points on a pattern
pub enum PyEndPoint {
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Draw a normal point
    Point(
        #[py_gen(name = "point", bridge = PyPoint)]
        Point
    ),
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Draw a point that matches the starting/ending color
    Match {
        radius: f32
    },
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Draw a point that matches the starting/ending color with a border
    BorderedMatch {
        match_radius: f32,
        #[py_gen(bridge = PyMarker)]
        border: Marker,
    }
}