import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'

function Dashboard() {
  const [employees, setEmployees] = useState([]);
  const [showForm, setShowForm] = useState(false); // Состояние: видна форма или нет
  const [newName, setNewName] = useState("");

  useEffect(() => {
    fetch('http://127.0.0.1:8000/employees')
      .then(res => res.json())
      .then(data => setEmployees(data));
  }, []);

  const handleAddEmployee = () => {
    // Логика отправки нового сотрудника на бэкенд
    fetch('http://127.0.0.1:8000/employees', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ full_name: newName, department: "New", position: "Staff" })
    })
    .then(res => res.json())
    .then(newEmp => {
      setEmployees([...employees, newEmp]); // Обновляем список без перезагрузки!
      setShowForm(true); // Прячем форму
    });
  };

  return (
    <div className="container">
      <header className="header">
        <h1>Employee Dashboard</h1>
        <button onClick={() => setShowForm(!showForm)} className="add-btn">
          {showForm ? "Cancel" : "Add Employee"}
        </button>
      </header>

      {showForm && (
        <div className="add-form">
          <input 
            value={newName} 
            onChange={(e) => setNewName(e.target.value)} 
            placeholder="Enter name" 
          />
          <button onClick={handleAddEmployee}>Save</button>
        </div>
      )}

      <section className="search-section">
        <input type="text" placeholder="Search by Name" />
        <button className="apply-btn">Apply</button>
      </section>

      <table className="employee-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Full Name</th>
            <th>Department</th>
            <th>Position</th>
            <th>Profile</th>
          </tr>
        </thead>
        <tbody>
          {employees.map(emp => (
            <tr key={emp.id}>
              <td>{emp.id}</td>
              <td>{emp.full_name}</td>
              <td>{emp.department}</td>
              <td>{emp.position}</td>
              <td><Link to={`/employee/${emp.id}`} className="open-btn">Open</Link></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function App() {
  return (
    <Router>
      <nav className="navbar">
        <Link to="/">Home</Link>
        <Link to="/dashboard">Dashboard</Link>
      </nav>

      <Routes>
        <Route path="/" element={<h2>Welcome to HR Portal</h2>} />
        <Route path="/dashboard" element={<Dashboard />} />
        {/* Здесь будет страница деталей сотрудника */}
        <Route path="/employee/:id" element={<h2>Employee Profile</h2>} />
      </Routes>
    </Router>
  )
}

export default App