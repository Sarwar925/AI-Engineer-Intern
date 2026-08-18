import React, { useState, useEffect } from 'react';
import { FaEdit, FaEye } from 'react-icons/fa'
import { FaTimes } from 'react-icons/fa';
import { FaTrash } from 'react-icons/fa';

// import axios from 'axios';

const Product = () => {
    const [products, setProducts] = useState([])
    const [selectProduct, setSelectProduct] = useState(null)
    const [showModel, setShowModel] = useState(false)
    const [showUpdate, setShowUpdate] = useState(false)
    const [showDelete, setShowDelete] = useState(false);
    const [deleteId, setDeleteId] = useState(null);
    const [deleteMessage, setDeleteMessage] = useState("");
    const [showProduct, setShowProduct] = useState(false);
    const [role, setRole] = useState(null);
    const [newProduct, setNewProduct] = useState({
        name:'',
        price:'',
        quantity:'',
        description:''
    })
    const canManageProducts = role === 'SuperAdmin' || role === 'Admin';
    const canDeleteProducts = role === 'SuperAdmin';

    useEffect(() => {
        fetch("http://127.0.0.1:8000/api/auth-check/", {
            method: "GET",
            credentials: "include",
        })
            .then((res) => res.json())
            .then((data) => {
                if (data.authenticated) {
                    setRole(data.role);
                }
            })
            .catch(() => setRole(null));
    }, []);

    // Fetching Products
    useEffect(() => {
        fetch('http://127.0.0.1:8000/api/products/')
            .then(res => res.json())
            .then(data => setProducts(data))
    }, [])

    // View Products
    const view_products = (id) => {
        fetch(`http://127.0.0.1:8000/api/product-view/${id}/`)
            .then(res =>  res.json())
            .then(data => {
                setSelectProduct(data);
                setShowModel(true)
            })
    }

    // Update Products
    const update_products = (id) => {
        fetch(`http://127.0.0.1:8000/api/product-view/${id}/`)
            .then(res => res.json())
            .then(data => {
                setSelectProduct(data)
                setShowUpdate(true)
            })
    }
    const handleChange = (e) => {
        setSelectProduct({
            ...selectProduct,
            [e.target.name]: e.target.value
        })

    }
    const save_update = () => {
        fetch(`http://127.0.0.1:8000/api/product-update/${selectProduct.id}/`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(selectProduct)
        })
            .then(() => {
                setShowUpdate(false)
                window.location.reload()
            })
    }
    
    // Delete Products
    const confirm_delete = () => {
        fetch(`http://127.0.0.1:8000/api/product-del/${deleteId}/`, { method: "DELETE" })
            .then(res => res.json())

            
            .then(() => {
                setDeleteMessage("Product Deleted Successfully");
                // Refresh products list
                fetch('http://127.0.0.1:8000/api/products/')
                    .then(res => res.json())
                    .then(data => setProducts(data))
                setShowDelete(true)
                setDeleteId(null)
            })
            window.location.reload()
    }

    const cancel_delete = () => {
        setShowDelete(false)
        setDeleteId(null)
    }

    //  Add Products
    const handleAddChange = (e)=>{
        setNewProduct({
            ...newProduct,
            [e.target.name]:e.target.value
        })
    }
    const save_product = ()=>{
        fetch('http://127.0.0.1:8000/api/add-product/',{
            method:'POST',
            headers:{
                'Content-Type':'application/json'
            },
            body:JSON.stringify(newProduct)
        })
        .then(res=>res.json())
        .then(()=>{
            setShowProduct(false)
            fetch('http://127.0.0.1:8000/api/add-product/')
            .then(res=>res.json())
            .then(data=>setProducts(data))
            window.location.reload()
        })
    }

    return (
        <div>
            <h1>Welcome to Product Page</h1>
            {canManageProducts && (
                <button
                    onClick={()=>setShowProduct(true)}
                    style={{
                    backgroundColor:'blue',
                    color:'white',
                    border:'none',
                    cursor:'pointer',
                    height:'25px',
                    borderRadius:'3px',
                    marginLeft:'1450px'
                    }}>
                    Add Product
                </button>
            )}
            <table style={tableStyle}>
                <thead>
                    <tr style={headerStyle}>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Price</th>
                        <th>Quantity</th>
                        <th>Description</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {products.map((p) => (
                        <tr key={p.id}>
                            <td>{p.id}</td>
                            <td>{p.name}</td>
                            <td>{p.price}</td>
                            <td>{p.quantity}</td>
                            <td>{p.description}</td>
                            <td>

                                <button onClick={() => view_products(p.id)} style={{ border: 'none', backgroundColor: 'white',color:'blue' }}><FaEye /></button>
                                {canManageProducts && (
                                    <button onClick={() => update_products(p.id)} style={{ border: 'none', backgroundColor: 'white',color:'orange' }}>
                                        <FaEdit />
                                    </button>
                                )}
                                {canDeleteProducts && (
                                    <button onClick={() => { setDeleteId(p.id); setShowDelete(true); }} style={{ color: 'red', border: 'none', background: 'transparent', cursor: 'pointer' }}>
                                        <FaTrash />
                                    </button>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
            
            {/* view products */}
            {showModel && selectProduct && (
            <div style={modalOverlayStyle} onClick={() => setShowModel(false)}>
                <div style={modalContentStyle}>
                    <button style={{marginLeft:'280px'}} onClick={() => setShowModel(false)}><FaTimes/></button>
                    <h2>{selectProduct.name}</h2>
                    <p><strong>Price:</strong> {selectProduct.price}</p>
                    <p><strong>Quantity:</strong> {selectProduct.quantity}</p>
                    <p><strong>Description:</strong> {selectProduct.description}</p>
                </div>
            </div>
            )
            }
            {/*  */}

            {/* update products */}
            {showUpdate && selectProduct && (
                <div style={modalOverlayStyle}>
                    <div style={modalContentStyle}>
                        <h2>Update Product</h2>
                        <input
                            name="name"
                            value={selectProduct.name}
                            onChange={handleChange}
                            placeholder="Name"
                        />
                        <br /><br />
                        <input
                            name="price"
                            value={selectProduct.price}
                            onChange={handleChange}
                            placeholder="Price"
                        />
                        <br /><br />
                        <input
                            name="quantity"
                            value={selectProduct.quantity}
                            onChange={handleChange}
                            placeholder="Quantity"
                        />
                        <br /><br />
                        <input
                            name="description"
                            value={selectProduct.description}
                            onChange={handleChange}
                            placeholder="Description"
                        />
                        <br /><br />
                        <button onClick={save_update}>Save</button>
                        <button onClick={() => setShowUpdate(false)}>Close</button>
                    </div>
                </div>
            )}
            {/*  */}

            {/* Delete Model */}
            {showDelete && (
                <div style={modalOverlayStyle} onClick={cancel_delete}>
                    <div style={modalContentStyle} onClick={e => e.stopPropagation()}>
                        <h2>Confirm Delete</h2>
                        <p>Are you sure you want to delete this product?</p>
                        <button onClick={confirm_delete} style={{ marginRight: '10px' }}>Yes</button>
                        <button onClick={cancel_delete}>No</button>
                    </div>
                </div>
            )}
            {deleteMessage && (
                <div style={{ backgroundColor: '#d4edda', color: '#155724', padding: '10px', margin: '10px 0', borderRadius: '5px' }}>
                    {deleteMessage}
                </div>
            )}

            {/* Add Product Model */}
            {showProduct && (

                <div style={modalOverlayStyle}>

                    <div style={modalContentStyle}>

                        <h2>Add Product</h2>

                        <input
                            name="name"
                            placeholder="Name"
                            onChange={handleAddChange}
                        />

                        <br /><br />

                        <input
                            name="price"
                            placeholder="Price"
                            onChange={handleAddChange}
                        />

                        <br /><br />

                        <input
                            name="quantity"
                            placeholder="Quantity"
                            onChange={handleAddChange}
                        />

                        <br /><br />

                        <input
                            name="description"
                            placeholder="Description"
                            onChange={handleAddChange}
                        />

                        <br /><br />

                        <button onClick={save_product}>
                            Save
                        </button>

                        <button onClick={() => setShowProduct(false)}>
                            Close
                        </button>

                    </div>

                </div>

            )}

        </div>
    )
}

const tableStyle = { width: '100%', borderCollapse: 'collapse', marginTop: '20px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' };
const headerStyle = { backgroundColor: '#4A90E2', color: 'white', textAlign: 'left', padding: '10px' };
// const rowStyle = { borderBottom: '1px solid #ddd' };
const modalOverlayStyle = {
    position: 'fixed',
    top: 0, left: 0, right: 0, bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000
};

const modalContentStyle = {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    width: '300px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.3)'
};


export default Product;
