use std::collections::{HashMap, HashSet};

use proc_macro2::{TokenStream, TokenTree};
use quote::{quote, ToTokens};
use syn::{Item, Result, Error, ItemFn, spanned::Spanned, Ident, Type, ReturnType, Pat, LitStr, Attribute, ItemStruct, ItemImpl, FnArg, Expr, Lit};

use crate::TypeArgs;


pub fn py_type_gen_impl(args: TypeArgs, input: Item) -> Result<TokenStream> {
    match input {
        Item::Fn(func) => type_fn(args, func),
        Item::Struct(struc) => type_struct(args, struc),
        Item::Impl(imp) => type_impl(args, imp),
        _ => Err(Error::new(input.span(), "expected impl block or function")),
    }
}

fn parse_pyo3_args(arg: &Vec<Attribute>) -> Result<HashMap<String, (Ident, Option<TokenTree>)>> {
    arg.iter()
        .map(parse_pyo3_arg)
        .collect::<Result<Vec<_>>>()?
        .into_iter()
        .fold(Ok(HashMap::<String, (Ident, Option<TokenTree>)>::new()), |acc, e| {
            let mut prev = acc?;

            for (key, val) in e {
                if let Some((ident, _)) = prev.get(&key) {
                    return Err(Error::new(ident.span(), format!("`{}` can onlyy be specified once", ident)))
                } else {
                    prev.insert(key, val);
                }
            }
            Ok(prev)
        })
}
fn parse_pyo3_arg(arg: &Attribute) -> Result<HashMap<String, (Ident, Option<TokenTree>)>> {
    let list = match &arg.meta {
        syn::Meta::List(list) => {
            list
        },
        _ => return Ok(HashMap::new()),
    };
    if list.path.segments[0].ident.to_string() != "pyo3" {
        return Ok(HashMap::new());
    }
    enum State {
        None,
        Ident(Ident),
        Equals(Ident),
        Comma,
    }
    let mut map = HashMap::new();
    let mut insert = |ident: Ident, token: Option<TokenTree>| -> Result<()>{
        if map.contains_key(&ident.to_string()) {
            Err(Error::new(ident.span(), format!("`{}` can only be specified once", ident)))
        } else {
            map.insert(ident.to_string(), (ident, token));
            Ok(())
        }
    };
    let mut state = State::None;
    for token in list.tokens.clone() {
        state = match state {
            State::None => {
                if let TokenTree::Ident(ident) = token {
                    State::Ident(ident)
                } else {
                    return Err(Error::new(token.span(), "expected identifier"))
                }
            },
            State::Ident(ident) => {
                if let TokenTree::Punct(punct) = token {
                    match punct.as_char() {
                        '=' => State::Equals(ident),
                        ',' => {
                            insert(ident, None)?;
                            State::Comma
                        }
                        _ => return Err(Error::new(punct.span(), "expected = or ,")),
                    }
                } else {
                    return Err(Error::new(token.span(), "expected = or ,"))
                }
            },
            State::Equals(ident) => {
                insert(ident, Some(token))?;
                State::Comma
            },
            State::Comma => {
                if let TokenTree::Punct(punct) = token {
                    if punct.as_char() != ',' {
                        return Err(Error::new(punct.span(), "expected ,"));
                    }
                } else {
                    return Err(Error::new(token.span(), "expected ,"));
                }
                State::None
            }
        }
    }
    match state {
        State::Ident(ident) => insert(ident, None)?,
        State::Equals(_) => return Err(Error::new_spanned(arg.clone(), "unfinished argument")),
        _ => (),
    }
    Ok(map)
}

fn type_fn(_args: TypeArgs, input: ItemFn) -> Result<TokenStream> {

    let name = &input.sig.ident; 
    let ret = &input.sig.output;

    let args = input.sig.inputs.iter().filter_map(|arg| {
        match arg {
            syn::FnArg::Receiver(_) => None,
            syn::FnArg::Typed(typ) => {
                Some((&*typ.pat, &*typ.ty))
            },
        }
    }).collect::<Vec<(&Pat, &Type)>>();



    let name = name.to_string();
    let ret = match ret {
        ReturnType::Default => quote!(()),
        ReturnType::Type(_, ty) => quote!(#ty),
    };

    let arg_types = args.iter().map(|(name, ty)| {
        let name = LitStr::new(&name.to_token_stream().to_string(), name.span());
        quote! {
            (
                #name,
                &<#ty as ::interface_macros::PyType>::path_string,
                &std::any::TypeId::of::<#ty>
            ),
        }
    }).collect::<TokenStream>();

    let type_checks = args.iter().map(|(_, ty)| {
        quote! {
            const _: () = ::interface_macros::check_pytype::<#ty>();
        }
    }).collect::<TokenStream>();

    let mut attributes = parse_pyo3_args(&input.attrs)?;
        
    let name = if let Some((ident, token)) = attributes.remove("name") {
        if let None = token {
            return Err(Error::new(ident.span(), "expected `name = \"<name>\"`"));
        }
        let token = token.unwrap();
        let lit = if let TokenTree::Literal(lit) = token {
            lit
        } else {
            return Err(Error::new(token.span(), "expected string literal"));
        };
        let st = lit.to_string();
        if &st[0..1] != "\"" {
            return Err(Error::new(lit.span(), "expected string literal"));
        }
        st[1..st.len()-1].to_string()
    } else {
        name
    };

    let doc_comments: Vec<String> = input.attrs.iter().flat_map(|attr| {
        match &attr.meta {
            syn::Meta::NameValue(name_val) => {
                //eprintln!("name_val: {:?}", name_val.path.get_ident());

                let Some(ident) = name_val.path.get_ident() else {
                    return vec![None]
                };
                if ident.to_string() != "doc" {
                    return vec![None]
                };
                let Expr::Lit(expr) = &name_val.value else {
                    return vec![None]
                };

                let Lit::Str(str) = &expr.lit else {
                    return vec![None]
                };
                str.value()
                    .split("\n")
                    .map(|a| Some(a.to_string()))
                    .collect()
               // name_val.\
            },
            _ => vec![None]
        }
    }).filter_map(|a| a)
    .collect();

    //eprintln!("comments: {:?}", doc_comments);
    let doc_comments = doc_comments.into_iter()
        .fold(TokenStream::new(), |mut acc, e| {
            acc.extend(quote!(#e,));
            acc
        });
    //eprintln!("hi: {:?}", doc_comments);

    Ok(quote! {
        #input

        #type_checks

        const _: () = ::interface_macros::check_pytype::<#ret>();

        #[cfg(test)]
        ::interface_macros::inventory::submit! {
            ::interface_macros::StoredPyTypes::new_func(
                #name,
                &[#doc_comments],
                &[#arg_types],
                &<#ret as ::interface_macros::PyType>::path_string,
                false
            )
        }
    })
}

fn type_struct(args: TypeArgs, input: ItemStruct) -> Result<TokenStream> {

    let py_path = if let Some(nested) = args.nested {
        quote! {
            const PATH: &'static [&'static ::core::primitive::str] = &{
                const PREV_PATH: &[&::core::primitive::str] = <#nested as ::interface_macros::PyPath>::PATH;
                let mut path: [&str; PREV_PATH.len()+1] = [""; PREV_PATH.len()+1];
                
                let mut i = 0;
                while i < PREV_PATH.len() {
                    path[i] = PREV_PATH[i];
                    i += 1;
                }
                //path[path.len()-1] = <#nested as ::pyo3::type_object::PyTypeInfo>::NAME;
                path[path.len()-1] = <#nested as ::interface_macros::PyPath>::NAME;
                path
            };
        }
    } else {
        quote! {}
    };

    let doc_comments = get_doc_comments(&input.attrs);

    
    let name = &input.ident;
    let properties = setup_type_properties(name);

    let py_type = if let Some(module_name) = &args.module {
        quote! {
            impl ::interface_macros::PyType for #name {

                //#py_path
                const PATH: &'static [&'static str] = <#name as ::interface_macros::PyPath>::PATH;
    
                fn to_string() -> String {
                   #module_name.to_string()
                }
                fn extend_string() -> String {
                    <::pyo3::PyAny as ::interface_macros::PyType>::path_string()
                }
            }
        }
    } else {
        quote! {
            impl ::interface_macros::PyType for #name {

                //#py_path
                const PATH: &'static [&'static str] = <#name as ::interface_macros::PyPath>::PATH;
    
                fn to_string() -> String {
                    <Self as ::pyo3::type_object::PyTypeInfo>::NAME.to_string()
                }
                fn extend_string() -> String {
                    <<Self as ::pyo3::impl_::pyclass::PyClassImpl>::BaseType as ::interface_macros::PyType>::path_string()
                }
            }
        }
    };

    let py_path_name = if let Some(name) = &args.module {
        quote!(#name)
    } else {
        quote!(<Self as ::pyo3::type_object::PyTypeInfo>::NAME)
    };

    let declarations: TokenStream = args.declarations.iter().map(|dec| {
        quote!(&#dec ,)
    }).collect();

    let new_function = if args.module.is_some() {
        quote!(new_module)
    } else {
        quote!(new_class)
    };

    let unions = args.unions.iter().map(|(name, union_parts)| {
        let parts = union_parts.iter()
            .map(|part| {
                let tmp = setup_type_properties(part);
                quote!(#tmp,)
            }).collect::<TokenStream>();
        
        quote!((#name, &[#parts]),)
    }).collect::<TokenStream>();

    Ok(quote! {
        #input

        #py_type

        impl ::interface_macros::PyPath for #name {
            #py_path
            const NAME: &'static str = #py_path_name;
        }

        #[cfg(test)]
        ::interface_macros::inventory::submit! {
            ::interface_macros::StoredPyTypes::#new_function(
                #properties,
                &[#doc_comments],
                &[#declarations],
                &[#unions]
            )
        }

    })
}

fn parse_type(ty: &mut Type, class: &Type) {
    match ty {
        Type::Array(arr) => {
            parse_type(&mut arr.elem, class);
        },
        Type::Path(path) => {
            //let seg = &mut path.path.segments[0];

            for seg in &mut path.path.segments {
                if seg.ident.to_string() == "Self" {
                    seg.ident = Ident::new(&class.to_token_stream().to_string(), seg.ident.span());
                    return;
                } 
                match &mut seg.arguments {
                    syn::PathArguments::None => (),
                    syn::PathArguments::AngleBracketed(paren) => {
                        for item in &mut paren.args {
                            match item {
                                syn::GenericArgument::Type(typ) => {
                                    parse_type(typ, class);
                                },
                                _ => (),
                            }
                        }
                    },
                    syn::PathArguments::Parenthesized(_) => (),
                }
            }
        },
        Type::Reference(re) => {
            parse_type(&mut re.elem, class);
        },
        Type::Slice(slice) => {
            parse_type(&mut slice.elem, class);
        },
        Type::Tuple(tup) => {
            for elm in &mut tup.elems {
                parse_type(elm, class);
            }
        },
        _ => (),
    }
}

fn get_doc_comments(attrs: &Vec<Attribute>) -> TokenStream {
    let doc_comments: Vec<String> = attrs.iter().flat_map(|attr| {
        match &attr.meta {
            syn::Meta::NameValue(name_val) => {
                //eprintln!("name_val: {:?}", name_val.path.get_ident());

                let Some(ident) = name_val.path.get_ident() else {
                    return vec![None]
                };
                if ident.to_string() != "doc" {
                    return vec![None]
                };
                let Expr::Lit(expr) = &name_val.value else {
                    return vec![None]
                };

                let Lit::Str(str) = &expr.lit else {
                    return vec![None]
                };
                str.value()
                    .split("\n")
                    .map(|a| Some(a.to_string()))
                    .collect()
               // name_val.\
            },
            _ => vec![None]
        }
    }).filter_map(|a| a)
    .collect();

    //eprintln!("comments: {:?}", doc_comments);
    doc_comments.into_iter()
        .fold(TokenStream::new(), |mut acc, e| {
            acc.extend(quote!(#e,));
            acc
        })
}
fn type_impl(_args: TypeArgs, input: ItemImpl) -> Result<TokenStream> {
    let mut to_check: Vec<Type> = Vec::new();
    let mut input = input;

    let class = &*input.self_ty;


    let funcs = input.items.iter_mut().filter_map(|item| {
        let func = match item {
            syn::ImplItem::Fn(func) => {
                func
            },
            _ => return Some(Err(Error::new_spanned(item.clone(), "only functions are supported"))),
        };

        let mut ignored = false;
        let mut tmp_attrs = Vec::new();

        ::std::mem::swap(&mut func.attrs, &mut tmp_attrs);

        func.attrs = tmp_attrs.into_iter().filter_map(|attr| {
            match &attr.meta {
                syn::Meta::Path(path) => {
                    if path.to_token_stream().to_string() == "ignore" {
                        ignored = true;
                        None
                    } else {
                        Some(attr)
                    }
                },
                _ => Some(attr)
            }
        }).collect();

        if ignored {
            return None;
        }


        let attrs: HashSet<String> = HashSet::from_iter(func.attrs.iter().filter_map(|attr| {
            //eprintln!("attr: {:?}", attr);
            match &attr.meta {
                syn::Meta::Path(path) => Some(path.to_token_stream().to_string()),
                _ => None
            }
        }));

        
        
        /*let parse_out = |ret: &ReturnType| -> TokenStream {
            
        };*/

        

        fn parse_out<'a, 'b>(ret: &'a ReturnType, to_check: &'b mut Vec<Type>, class: &Type) -> TokenStream {
            match ret {
                ReturnType::Default => quote!(()),
                ReturnType::Type(_, ty) => {
                    let mut ty = *ty.clone();
                    parse_type(&mut ty, class);
                    to_check.push(ty.clone());
                    quote!(#ty)
                },
            }
        }


        fn parse_args<'a, 'b>(args: Vec<&'a FnArg>, to_check: &'b mut Vec<Type>, class: &Type) -> TokenStream {
            args.iter().map(|arg| {
                let pat = match arg {
                    syn::FnArg::Receiver(_) => unreachable!("hi?"),
                    syn::FnArg::Typed(ty) => ty,
                };
                let name = pat.pat.to_token_stream().to_string();
                let mut ty = *pat.ty.clone();
                parse_type(&mut ty, class);

                to_check.push(ty.clone());
                quote!{
                    (
                        #name,
                        &<#ty as ::interface_macros::PyType>::path_string,
                        &std::any::TypeId::of::<#ty>
                    ),
                }
            }).collect::<TokenStream>()
        }
        
        let mut inner_check = Vec::new();
        let (name, ret, args, slf) = if attrs.contains("new") {
            (
                "__init__".to_string(),
                quote!(()),
                parse_args(func.sig.inputs.iter().collect(), &mut inner_check, class),
                true
            )
        } else {
            (
                func.sig.ident.to_string(),
                parse_out(&func.sig.output, &mut inner_check, class),
                parse_args(func.sig.inputs.iter().skip(1).collect(), &mut inner_check, class),
                true
            )
        };
        
        to_check.append(&mut inner_check);

        let typ = if attrs.contains("getter") {
            quote!(::interface_macros::PyFuncType::Property)
        } else {
            quote!(::interface_macros::PyFuncType::Normal)
        };

        let doc_comments = get_doc_comments(&func.attrs);
        Some(Ok(quote!{
            &::interface_macros::PyFunc {
                name: #name,
                comments: &[#doc_comments],
                args: &[#args],
                ret: &<#ret as ::interface_macros::PyType>::path_string,
                slf: #slf,
                typ: #typ
            },
        }))
    }).collect::<Result<TokenStream>>()?;

    //eprintln!("\n\nfuncs: {}", funcs);

    let type_checks = to_check.into_iter().map(|ty| {
        quote! {
            const _: () = ::interface_macros::check_pytype::<#ty>();
        }
    }).collect::<TokenStream>();

    let properties = setup_type_properties(class);
    Ok(quote! {
        #input

        #[cfg(test)]
        ::interface_macros::inventory::submit! {
            ::interface_macros::StoredPyTypes::new_impl(
                #properties,
                &[ #funcs ],
            )
        }
        #type_checks
    })
}

fn setup_type_properties<T: ToTokens>(item: &T) -> TokenStream {
    quote! {
        ::interface_macros::TypeProperties {
            name: &<#item as ::interface_macros::PyType>::to_string,
            name_path: &<#item as ::interface_macros::PyType>::path_string,
            extend: &<#item as ::interface_macros::PyType>::extend_string,
            path: <#item as ::interface_macros::PyType>::PATH,
            type_id: &::std::any::TypeId::of::<#item>
        }
    }
}