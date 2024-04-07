
use proc_macro2::{Span, TokenStream, Literal};
use syn::{Item, Error, Result, Ident, Type, Token, LitStr, Attribute, ItemStruct, ItemEnum, Fields, spanned::Spanned, Field, parse::Parse};
use quote::{quote, ToTokens};

use crate::Arguments;

pub fn py_gen_impl(args: Arguments, input: Item) -> Result<TokenStream> {

    match input {
        Item::Enum(enu) => {
            //py_gen_enum(args, enu)
            py_gen_enum(args, enu)
        },
        Item::Struct(struc) => py_gen_struct(args, struc),
        _ => Err(Error::new(Span::call_site(), "expected enum or struct")),
    }
}

fn get_comments(attrs: &Vec<Attribute>) -> Vec<Attribute> {
    attrs.iter()
    .filter_map(|attr| {
        let name_val = match &attr.meta {
            syn::Meta::NameValue(name_val) => name_val,
            _ => return None,
        };

        if name_val.path.segments[0].ident.to_string() != "doc"{
            return None;
        }

        Some(attr.clone())
    }).collect()
}

fn gen_into_froms(
    into_name: TokenStream, 
    from_name: TokenStream, 
    into_struct: TokenStream, 
    from_struct: TokenStream, 
    fields: &Fields, 
    field_attrs: &Vec<PyField>,
    add_dot: bool
) -> (TokenStream, TokenStream) {
    let (intos, froms): (Vec<TokenStream>, Vec<TokenStream>) = field_attrs.iter().zip(fields.iter()).map(|(field_attr, field)| {

        let (into, from) = (
            if add_dot {
                field_attr.field_name.prepend(into_name.clone())
            } else {
                field_attr.field_name.prepend_no_dot(into_name.clone())
            },
            field_attr.field_name.prepend(from_name.clone())
        );

        match &field_attr.convert {
            Some(convert) => {
                let ty = &field.ty;
                (
                    quote!(<#convert as ::interface_macros::PyBridge<#ty>>::into_py(#into, _py)?),
                    quote!(<#convert as ::interface_macros::PyBridge<#ty>>::from_py(#from, _py)?)
                )
            },
            None => {
                (into, from)
            },
        }
    }).unzip();
    
    let (into, from) = match &fields {
        Fields::Named(_) => {
            let into = intos.iter().zip(field_attrs.iter()).map(|(into, field)| {
                let field_name = match &field.field_name {
                    FieldName::Num(_) => unreachable!(),
                    FieldName::Name(name) => name,
                };
                quote!(#field_name: #into,)
            }).collect::<TokenStream>();
            let from = froms.iter().zip(field_attrs.iter()).map(|(from, field)| {
                let field_name = match &field.field_name {
                    FieldName::Num(_) => unreachable!(),
                    FieldName::Name(name) => name,
                };
                quote!(#field_name: #from,)
            }).collect::<TokenStream>();

            (
                quote!(#into_struct { #into }),
                quote!(#from_struct { #from })
            )

        },
        Fields::Unnamed(_) => {
            let into: TokenStream = intos.iter().map(|a| quote!(#a,)).collect();
            let from: TokenStream = froms.iter().map(|a| quote!(#a,)).collect();

            (
                quote!(#into_struct (#into)),
                quote!(#from_struct (#from))
            )
        },
        Fields::Unit => {
            (
                quote!(#into_struct),
                quote!(#from_struct)
            )
        },
    };

    (into, from)
}
fn py_gen_struct(args: Arguments, input: ItemStruct) -> Result<TokenStream> {
    let ident = input.ident;
    let mut fields = input.fields;
    let mut attrs = input.attrs;

    let field_attrs = gen_field_attrs(&mut fields)?;

    let name = match &args.bridge {
        Some(bridge) => bridge.to_string(),
        None => ident.to_string(),
    };

    let py_methods = gen_py_methods(&ident, &mut fields, &field_attrs, &mut attrs, &name)?;
    
    let semi = input.semi_token;
    let attrs = TokenStream::from_iter(attrs.into_iter().map(|a| a.to_token_stream()));
    

    let bridge = args.bridge.map(|bridge| {

        let (into, from) = gen_into_froms(quote!(self), quote!(val), quote!(#ident), quote!(Self), &fields, &field_attrs, true);
        quote!{
            impl ::interface_macros::PyBridge<#ident> for #bridge {
                type PyOut = #ident;

                fn into_py(self, _py: ::pyo3::Python) -> ::pyo3::PyResult<Self::PyOut> {
                    Ok(#into)
                }
                fn from_py(val: #ident, _py: ::pyo3::Python) -> ::pyo3::PyResult<Self> {
                    Ok(#from)
                }
            }
        }
    });


    let vis = &input.vis;
    Ok(quote!{
        #attrs
        #[::interface_macros::py_type_gen]
        #[::pyo3::pyclass(name = #name)]
        #vis struct #ident #fields #semi

        #[::interface_macros::py_type_gen]
        #[::pyo3::pymethods]
        #py_methods

        #bridge
    })
}

fn py_gen_enum(args: Arguments, input: ItemEnum) -> Result<TokenStream> {
    let mut input = input;
    let module_ident = Ident::new(&format!("{}Module", input.ident.to_string()), input.ident.span());

    let variant_idents = input.variants.iter().map(|variant| {
        Ident::new(&format!("{}{}", input.ident.to_string(), variant.ident.to_string()), variant.span())
    }).collect::<Vec<Ident>>();

    let field_args = input.variants.iter_mut().map(|variant| {
        gen_field_attrs(&mut variant.fields)
    }).collect::<Result<Vec<_>>>()?;
    
    let sub_structs = input.variants
    .iter_mut()
    .zip(variant_idents.iter())
    .zip(field_args.iter())
    .map(|((variant, ident), field_attrs)| {
        //let variant = variant.clone();
        //let ident = variant.ident;

        //let field_attrs = gen_field_attrs(&mut fields)?;

        let py_methods = gen_py_methods(&ident, &mut variant.fields, &field_attrs, &mut variant.attrs, &variant.ident.to_string())?;

        let semi = match &variant.fields {
            Fields::Named(_) => None,
            Fields::Unnamed(_)
            | Fields::Unit => Some(quote!(;)),
        };
        let attrs = TokenStream::from_iter(variant.attrs.iter().map(|a| a.to_token_stream()));

        let fields = &variant.fields;

        let mut name = format!("{}", variant.ident.to_string());
        if name == "None" {
            name = "None_".to_string();
        }

        //let inp_ident = &input.ident;
        let vis = &input.vis;
        Ok(quote! {
            #attrs
            #[::interface_macros::py_type_gen(nested = #module_ident)]
            #[::pyo3::pyclass(name = #name)]
            #vis struct #ident #fields #semi
            
            #[::interface_macros::py_type_gen]
            #[::pyo3::pymethods]
            #py_methods
        })
    }).collect::<Result<TokenStream>>()?;

    let ident = &input.ident;

    let enum_fields = input.variants.iter().zip(variant_idents.iter()).map(|(variant, variant_ident)| {
        let ident = &variant.ident;
        quote!(#ident(#variant_ident),)
    }).collect::<TokenStream>();

    let into_py_match = input.variants.iter().zip(variant_idents.iter()).map(|(variant, variant_struct_ident)| {
        let variant_ident = &variant.ident;
        quote!(#ident::#variant_ident(a) => <#variant_struct_ident as ::pyo3::IntoPy<::pyo3::Py<::pyo3::PyAny>>>::into_py(a, py),)
    }).collect::<TokenStream>();

    let bridge = args.bridge.clone().map(|bridge| {

        let (into, from): (TokenStream, TokenStream) = input
        .variants
        .iter()
        .zip(variant_idents.iter())
        .zip(field_args.iter())
        .map(|((variant, variant_struct_ident), field_attrs)| {
            
            let variant_ident = &variant.ident;
            let fields = &variant.fields;

            //let field_attrs = gen_field_attrs(&mut fields).unwrap();

            let (into, from) = gen_into_froms(quote!(a), quote!(a), quote!(#variant_struct_ident), quote!(Self::#variant_ident), &fields, &field_attrs, false);


            let breakdown = match &variant.fields {
                Fields::Named(_) => {
                    let fields: TokenStream = variant.fields.iter().map(|field| {
                        let ident = field.ident.clone().unwrap();
                        let new_ident = Ident::new(&format!("a{}", ident), ident.span());
                        quote!(#ident: #new_ident,)
                    }).collect();

                    quote!({ #fields })
                },
                Fields::Unnamed(_) => {
                    let fields: TokenStream = variant.fields.iter().enumerate().map(|(i, field)| {
                        let ident = Ident::new(&format!("a{i}"), field.span());
                        quote!(#ident,)
                    }).collect();
                    quote!( (#fields) )
                },
                Fields::Unit => quote!(),
            };

            let into = quote!(Self :: #variant_ident #breakdown => #ident :: #variant_ident(#into),);

            let from = quote!(#ident :: #variant_ident(a) => #from,);
            
            (into, from)
        }).unzip();

        quote! {
            impl ::interface_macros::PyBridge<#ident> for #bridge {
                type PyOut = #ident;

                fn into_py(self, _py: ::pyo3::Python) -> ::pyo3::PyResult<Self::PyOut> {
                    Ok(match self {
                        #into
                    })
                }
                fn from_py(val: #ident, _py: ::pyo3::Python) -> ::pyo3::PyResult<Self> {
                    Ok(match val {
                        #from
                    })
                }
            }
        }
    });

    
    let py_path_name = if let Some(bridge) = &args.bridge {
        bridge.to_string()
    } else {
        input.ident.to_string()
    };

    let py_type_str = variant_idents.iter().fold(None, |acc, e| {
        let (str, mut args) = if let Some((str, args)) = acc {
            (format!("{str} | {{}}"), args)
        } else {
            (format!("{{}}"),TokenStream::new())
        };

        args.extend(quote!(
            <#e as ::interface_macros::PyType>::path_string(),
        ));

        Some((str, args))
    });

    let any_type_name = format!("Any{}", py_path_name.to_string());
    let py_type = if py_type_str.is_some() {
        Some(quote! {
            impl ::interface_macros::PyType for #ident {
                const PATH: &'static [&'static ::core::primitive::str] = &{
                    const PREV_PATH: &[&::core::primitive::str] = <#module_ident as ::interface_macros::PyPath>::PATH;
                    let mut path: [&str; PREV_PATH.len()+1] = [""; PREV_PATH.len()+1];
                    
                    let mut i = 0;
                    while i < PREV_PATH.len() {
                        path[i] = PREV_PATH[i];
                        i += 1;
                    }
                    path[path.len()-1] = <#module_ident as ::interface_macros::PyPath>::NAME;
                    path
                };
                fn to_string() -> String {
                    #any_type_name.to_string()
                }
            }
        })
    } else {
        None
    };

    let union_parts = variant_idents.iter().map(|ident| {
        quote!(#ident,)
    }).collect::<TokenStream>();

    let vis = &input.vis;
    let attrs: TokenStream = get_comments(&input.attrs).iter().map(|a| a.to_token_stream()).collect();
    
    Ok(quote!{


        #[::interface_macros::py_type_gen(module = #py_path_name, union = (#any_type_name, [#union_parts]))]
        #attrs
        #vis struct #module_ident;
        
        #[derive(::pyo3::FromPyObject)]
        #vis enum #ident {
            #enum_fields
        }

        impl ::pyo3::IntoPy<::pyo3::Py<::pyo3::PyAny>> for #ident {
            fn into_py(self, py: ::pyo3::Python<'_>) -> ::pyo3::Py<::pyo3::PyAny> {
                match self {
                    #into_py_match
                }
            }
        }

        #bridge

        //impl ::interface_macros::PyPath for #ident {
        //    const NAME: &'static str = #py_path_name;
        //}

        #py_type
        

        #sub_structs
    })
}


const ATTR_PATH: &str = "py_gen";

enum FieldName {
    Num(usize),
    Name(Ident)
}

impl FieldName {
    fn prepend(&self, prepend: TokenStream) -> TokenStream {
        match self {
            FieldName::Num(num) => {
                let num = Literal::usize_unsuffixed(*num);
                quote!(#prepend.#num)
            },
            FieldName::Name(name) => {
                quote!(#prepend.#name)
            },
        }
    }

    fn prepend_no_dot(&self, prepend: TokenStream) -> TokenStream {
        match self {
            FieldName::Num(num) => {
                let ident = Ident::new(&format!("{}{}", prepend.to_string(), num), Span::call_site());
                quote!(#ident)
            },
            FieldName::Name(name) => {
                let ident = Ident::new(&format!("{}{}", prepend.to_string(), name), name.span());
                quote!(#ident)
            },
        }
    }
}

struct PyField {
    name: Ident,
    field_name: FieldName,
    bridge: Option<Type>,
    convert: Option<Type>,
    comments: Vec<Attribute>,
}

struct PyFieldBuilder {
    name: Option<Ident>,
    bridge: Option<Type>,
    convert: Option<Type>,
    comments: Vec<Attribute>,
}

impl Parse for PyFieldBuilder {
    fn parse(input: syn::parse::ParseStream) -> Result<Self> {
        let mut builder = Self::new();
        loop {
            /*let ident = match tokens.next() {
                Some(ident) => ident,
                None => break,
            };*/
            if input.is_empty() {
                break;
            }


            /*let ident: Ident = syn::parse2(ident.clone().into())
                .map_err(|_| Error::new(ident.span(), "Expected an ident"))?;*/

            let ident: Ident = input.parse()?;

            /*let equals = tokens.next()
                .ok_or(Error::new(ident.span(), "Expected `<ident> = <item>`"))?;

            let _equals: Token![=] = syn::parse2(equals.clone().into())
                .map_err(|_| Error::new(equals.span(), "Expected `=`"))?;*/
            input.parse::<Token![=]>()?;

            /*let next = tokens.next()
                .ok_or(Error::new(equals.span(), "Expected `<ident> = <item>`"))?;*/

            match &ident.to_string()[..] {
                "name" => {
                    if builder.name.is_some() {
                        return Err(Error::new(ident.span(), "can't have more than one name"));
                    }

                    /*let name: LitStr = syn::parse2(next.clone().into())
                        .map_err(|_| Error::new(next.span(), "Expected `str`"))?;*/
                    let name: LitStr = input.parse()?;

                    let name = Ident::new(&name.value(), name.span());
                    builder.name = Some(name);
                },
                "bridge" => {
                    if builder.bridge.is_some() {
                        return Err(Error::new(ident.span(), "can't have more than one bridge"));
                    }

                    /*let ty: Type = syn::parse2(next.clone().into())
                        .map_err(|_| Error::new(next.span(), "Expected `type`"))?;*/

                    let ty: Type = input.parse()?;

                    builder.bridge = Some(ty);
                },
                "convert" => {
                    if builder.convert.is_some() {
                        return Err(Error::new(ident.span(), "can't have more than one convert"));
                    }

                    /*let ty: Type = syn::parse2(next.clone().into())
                        .map_err(|_| Error::new(next.span(), "Expected `type`"))?;*/
                    let ty: Type = input.parse()?;

                    builder.convert = Some(ty);
                },
                _ => return Err(Error::new(ident.span(), "unkown attribute"))
            }

            /*match tokens.next() {
                Some(comma) => {
                    syn::parse2::<Token![,]>(comma.clone().into())
                        .map_err(|_| Error::new(comma.span(), "Expected `,`"))?;
                },
                None => break,
            }*/
            if input.is_empty() {
                break;
            } else {
                input.parse::<Token![,]>()?;
            }

        }
        Ok(builder)
    }
    
}
impl PyFieldBuilder {
    fn new() -> Self {
        Self {
            name: None,
            bridge: None,
            convert: None,
            comments: Vec::new()
        }
    }

    fn try_to_comment(value: &Attribute) -> Option<Self> {
        let name_val = match &value.meta {
            syn::Meta::NameValue(name_val) => name_val,
            _ => return None,
        };

        if name_val.path.segments[0].ident.to_string() != "doc" {
            return None;
        }

        Some(
            Self {
                name: None,
                bridge: None,
                convert: None,
                comments: vec![value.clone()]
            }
        )
    }

    fn try_from_attribute(value: &Attribute) -> Result<Option<Self>> {
        let list = match &value.meta {
            syn::Meta::List(list) => list,
            _ => return Ok(Self::try_to_comment(value)),
        };

        if list.path.segments[0].ident.to_string() != ATTR_PATH {
            return Ok(None);
        }

        //let mut tokens = list.tokens.clone().into_iter();

        //let mut builder = PyFieldBuilder::new();
        
        let builder = syn::parse2(list.tokens.clone())?;


        Ok(Some(builder))
    }

    fn build(fields: Vec<Self>, default_name: Ident, field_name: FieldName, comments: Vec<Attribute>) -> Result<PyField> {
        let mut py_field = PyField {
            name: default_name,
            field_name,
            bridge: None,
            convert: None,
            comments
        };

        let mut defined_name = false;

        for mut field in fields {
            if let Some(name) = field.name {
                if defined_name {
                    return Err(Error::new(name.span(), "Can't have more than one name"))
                }
                defined_name = true;
                py_field.name = name;
            }

            if let Some(bridge) = field.bridge {
                if py_field.bridge.is_some() {
                    return Err(Error::new(bridge.span(), "Can't have more than one bridge"));
                }

                py_field.bridge = Some(bridge);
            }
            if let Some(convert) = field.convert {
                if py_field.convert.is_some() {
                    return Err(Error::new(convert.span(), "Can't have more than one convert"));
                }

                py_field.convert = Some(convert);
            }

            py_field.comments.append(&mut field.comments)
        }

        match (&py_field.bridge, &py_field.convert) {
            (Some(bridge), Some(_)) => {
                return Err(Error::new(bridge.span(), "can't have a bridge and convert!"))
            },
            _ => ()
        }
        
        Ok(py_field)

    }
}



fn parse_field_attrs(attrs: &mut Vec<Attribute>, default_name: Ident, field_name: FieldName) -> Result<PyField> {
    let mut old_attrs: Vec<Attribute> = vec![];
    std::mem::swap(attrs, &mut old_attrs);

    let fields = old_attrs.into_iter().filter_map(|a| {
        match PyFieldBuilder::try_from_attribute(&a) {
            Ok(ok) => {
                match ok {
                    Some(field) => Some(Ok(field)),
                    None => {
                        attrs.push(a);
                        None
                    },
                }
            },
            Err(err) => Some(Err(err)),
        }
    }).collect::<Result<Vec<_>>>()?;


    PyFieldBuilder::build(fields, default_name, field_name, vec![])
} 

fn gen_new(fields: &Fields, field_attrs: &Vec<PyField>, comments: &Vec<Attribute>) -> TokenStream {

    let args = fields.iter()
        .zip(field_attrs.iter())
        .map(|(field, attrs)| {
            let ty = match &attrs.bridge {
                Some(bridge) => bridge,
                None => &field.ty
            };
            let name = &attrs.name;
            quote!(#name: #ty,)
        }).collect::<TokenStream>();
    
    let names = field_attrs.iter().zip(fields.iter()).map(|(field_attr, field)| {
        let name = &field_attr.name;
        let ty = &field.ty;

        match &field_attr.bridge {
            Some(bridge) => {
                quote!(<#ty as ::interface_macros::PyBridge<#bridge>>::from_py(#name, py)?)
            },
            None => {
                quote!(#name)
            },
        }
    }).collect::<Vec<TokenStream>>();

    let initializer = match &fields {
        Fields::Named(named) => {
            let fields = named.named
                .iter()
                .zip(names.iter())
                .map(|(field, inp_name)| {
                    let field_name = field.ident.clone().unwrap();

                    quote!(#field_name : #inp_name,)
                }).collect::<TokenStream>();
            
            quote! {
                Self {
                    #fields
                }
            }
        },
        Fields::Unnamed(_) => {
            let fields = names.iter().map(|name| {
                quote!(#name,)
            }).collect::<TokenStream>();

            quote!(Self(#fields))
        },
        Fields::Unit => quote!(Self),
    };

    let comments: TokenStream = comments.iter().map(|a| a.to_token_stream()).collect();

    let param_comments: TokenStream = field_attrs.iter().filter_map(|attr| {
        let comment = if let Some(val) = attr.comments.get(0) {
            let name_val = match &val.meta {
                syn::Meta::NameValue(name_val) => name_val,
                _ => unreachable!()
            };

            name_val.value.to_token_stream().to_string()
        } else {
            return None;
        };

        let comment = &comment[1..comment.len()-1];

        let field_name = attr.name.to_string();

        let doc_str = format!(":param {}: {}", field_name, comment);
        //let doc_str = "";
        Some(quote!(#[doc = #doc_str]))
    }).collect();
    quote!{
        #[new]
        #comments
        #param_comments
        fn new(py: ::pyo3::Python, #args) -> ::pyo3::PyResult<Self> {
            Ok(#initializer)
        }
    }
}

fn gen_getter(field: &Field, attr: &PyField) -> TokenStream {

    let get_ident = Ident::new(&format!("get_{}", attr.name.to_string()), attr.name.span());

    let getter = attr.field_name.prepend(quote!(self));

    let ty = &field.ty;

    let comments = attr.comments
        .iter()
        .map(|a| a.to_token_stream())
        .collect::<TokenStream>();

    match &attr.bridge {
        Some(bridge) => {
            quote!{
                #[getter]
                #comments
                fn #get_ident(&self, py: ::pyo3::Python) -> ::pyo3::PyResult<<#ty as ::interface_macros::PyBridge<#bridge>>::PyOut> {
                    <#ty as ::interface_macros::PyBridge<#bridge>>::into_py(#getter.clone(), py)
                }
            }
        },
        None => {
            quote!{
                #[getter]
                #comments
                fn #get_ident(&self) -> #ty {
                    #getter.clone()
                }
            }
        }
    }
}

fn gen_with(field: &Field, attr: &PyField) -> TokenStream {

    let with_ident = Ident::new(&format!("with_{}", attr.name.to_string()), attr.name.span());

    let attr_name = &attr.name;

    let with = attr.field_name.prepend(quote!(val));

    let ty = &field.ty;
    match &attr.bridge {
        Some(bridge) => {
            quote! {
                fn #with_ident(&self, #attr_name: #bridge, py: ::pyo3::Python) -> ::pyo3::PyResult<Self> {
                    let mut val = self.clone();
                    #with = <#ty as ::interface_macros::PyBridge<#bridge>>::from_py(#attr_name, py)?;

                    Ok(val)
                }
            }
        },
        None => {
            quote! {
                fn #with_ident(&self, #attr_name: #ty) -> Self {
                    let mut val = self.clone();
                    #with = #attr_name;
        
                    val
                }
            }
        },
    }
    
}

fn gen_field_attrs(fields: &mut Fields) -> Result<Vec<PyField>> {
    fields.iter_mut().enumerate().map(|(index, field)| {
        let default_name = field.ident.clone().unwrap_or(
            Ident::new(&format!("a{index}"), field.span())
        );
        let field_name = match &field.ident {
            Some(val) => FieldName::Name(val.clone()),
            None => FieldName::Num(index),
        };
        
        parse_field_attrs(&mut field.attrs, default_name, field_name)
    }).collect()
}
fn gen_py_methods(ident: &Ident, fields: &mut Fields, field_attrs: &Vec<PyField>, attrs: &mut Vec<Attribute>, variant_name: &str) -> Result<TokenStream> {

    let comments = get_comments(attrs);

    let new_func = gen_new(&fields, &field_attrs, &comments);

    let getters = fields.iter().zip(field_attrs.iter()).map(|(field, attrs)| {
        gen_getter(field, attrs)
    }).collect::<TokenStream>();

    let withs = fields.iter().zip(field_attrs.iter()).map(|(field, attrs)| {
        gen_with(field, attrs)
    }).collect::<TokenStream>();

    let rust_name_len = ident.to_string().len();

    let repr = quote! {
        #[ignore]
        fn __repr__(&self) -> String {
            let mut out = format!("{:?}", self);

            #variant_name.to_string() + &out[#rust_name_len..]
        }
    };
    let rich_cmp = quote! {
        #[ignore]
        fn __richcmp__(&self, other: &Self, op: ::pyo3::basic::CompareOp) -> ::pyo3::PyResult<bool> {
            Ok(match op {
                ::pyo3::pyclass::CompareOp::Lt => self < other,
                ::pyo3::pyclass::CompareOp::Le => self <= other,
                ::pyo3::pyclass::CompareOp::Eq => self == other,
                ::pyo3::pyclass::CompareOp::Ne => self != other,
                ::pyo3::pyclass::CompareOp::Gt => self > other,
                ::pyo3::pyclass::CompareOp::Ge => self >= other,
            })
        }
    };

    Ok(quote! {
        impl #ident {
            #new_func

            #getters

            #withs

            #repr

            #rich_cmp
        }
        
    })
}