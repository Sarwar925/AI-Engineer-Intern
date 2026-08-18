import React, { useEffect, useState } from "react";
import axios from "axios";

function Home() {
  const [data, setData] = useState({});

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem("token");

        const res = await axios.get(
          "http://127.0.0.1:8000/api/dashboard/",
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        setData(res.data);
      } 
      catch (error) {
        // alert("Unauthorized");
      }
    };

    fetchDashboard();
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      <p>{data.message}</p>
      <p>User: {data.username}</p>
      <p>Email: {data.email}</p>
    </div>
  );
}

export default Home;
