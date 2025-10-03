import React, { useState, useEffect, useCallback } from 'react';

//=========== API Client ===========//
const apiClient = {
  async request(endpoint, { body, token, ...customConfig }) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    const config = {
      method: body ? 'POST' : 'GET',
      ...customConfig,
      headers: { ...headers, ...customConfig.headers },
    };
    if (body) {
      config.body = body;
    }
    const response = await fetch(`http://127.0.0.1:8000${endpoint}`, config);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      return Promise.reject(errorData);
    }
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.indexOf("application/json") !== -1) {
      return response.json();
    }
  },
};


//=========== LoginPage Component ===========//
function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('Admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    try {
      const data = await apiClient.request('/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString(),
      });
      onLogin(data.access_token);
    } catch (err) {
      setError(err.detail || 'Failed to login.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1 className="auth-title">Meeting Agent</h1>
        <p className="auth-subtitle">Log in to continue</p>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label htmlFor="username">Username</label>
            <input type="text" id="username" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </div>
          <div className="input-group">
            <label htmlFor="password">Password</label>
            <input type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          {error && <p className="error-message">{error}</p>}
          <button type="submit" className="auth-button" disabled={isLoading}>
            {isLoading ? 'Logging In...' : 'Login'}
          </button>
        </form>
         <div className="demo-credentials">
            <p><strong>Demo Users:</strong></p>
            <ul>
                <li>Priya (pw: priya123)</li>
                <li>Admin (pw: admin123)</li>
            </ul>
        </div>
      </div>
    </div>
  );
}


//=========== Dashboard Components ===========//
const UserTaskItem = ({ task }) => (
    <div className="task-item">
        <span className={`status-indicator status-${task.status.toLowerCase().replace(' ', '-')}`}></span>
        <div className="task-details">
            <p className="task-description">{task.description}</p>
            {task.due_date && <p className="task-due-date">Due: {task.due_date}</p>}
        </div>
        <span className="task-status">{task.status}</span>
    </div>
);

const AdminTaskItem = ({ task, onUpdateStatus }) => (
    <div className="task-item admin-task-item">
        <div className="task-details">
            <p className="task-description">{task.description}</p>
            <p className="task-assignee">Assigned to: <strong>{task.assignee.username}</strong></p>
            {task.due_date && <p className="task-due-date">Due: {task.due_date}</p>}
        </div>
        <div className="task-actions">
            <select value={task.status} onChange={(e) => onUpdateStatus(task.id, e.target.value)} className="status-select">
                <option value="To Do">To Do</option>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
                <option value="Verified">Verified</option>
            </select>
        </div>
    </div>
);

const AdminDashboard = ({ token }) => {
    const [tasks, setTasks] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    const fetchAllTasks = useCallback(async () => {
        setIsLoading(true);
        try {
            const allTasks = await apiClient.request('/admin/tasks', { token });
            setTasks(allTasks);
        } catch (err) {
            setError(err.detail || 'Failed to fetch tasks.');
        } finally {
            setIsLoading(false);
        }
    }, [token]);

    useEffect(() => { fetchAllTasks(); }, [fetchAllTasks]);

    const handleUpdateStatus = async (taskId, newStatus) => {
        try {
            await apiClient.request(`/admin/tasks/${taskId}`, {
                token, method: 'PATCH', body: JSON.stringify({ status: newStatus }),
            });
            fetchAllTasks();
        } catch (err) {
            setError(err.detail || `Failed to update task ${taskId}.`);
        }
    };
    
    return (
        <div className="card tasks-card admin-view">
            <h2>Admin Panel: All Tasks</h2>
            {error && <p className="error-message">{error}</p>}
            {isLoading ? <p>Loading all tasks...</p> : (
                <div className="task-list">
                    {tasks.length > 0 ? (
                       tasks.map(task => <AdminTaskItem key={task.id} task={task} onUpdateStatus={handleUpdateStatus} />)
                    ) : ( <p className="no-tasks-message">No tasks found across all users.</p> )}
                </div>
            )}
        </div>
    );
};

const UserDashboard = ({ token, user }) => {
    const [userTasks, setUserTasks] = useState([]);
    const [error, setError] = useState('');
    const [isLoadingTasks, setIsLoadingTasks] = useState(true);
    const [file, setFile] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [processResult, setProcessResult] = useState(null);
    const [uploadError, setUploadError] = useState('');

    const fetchUserTasks = useCallback(async () => {
        setIsLoadingTasks(true);
        try {
            const fetchedTasks = await apiClient.request('/users/me/tasks', { token });
            setUserTasks(fetchedTasks);
        } catch (err) {
            setError(err.detail || 'Failed to fetch tasks.');
        } finally {
            setIsLoadingTasks(false);
        }
    }, [token]);

    useEffect(() => { fetchUserTasks() }, [fetchUserTasks]);

    const handleFileUpload = async (e) => {
        e.preventDefault();
        if (!file) { setUploadError('Please select a file first.'); return; }
        setIsProcessing(true);
        setUploadError('');
        setProcessResult(null);

        const formData = new FormData();
        formData.append('file', file);
        try {
            const response = await fetch('http://127.0.0.1:8000/process-audio/', {
                method: 'POST', body: formData, headers: { 'Authorization': `Bearer ${token}` },
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'File processing failed.');
            }
            const result = await response.json();
            setProcessResult(`Processing complete! ${result.created_tasks} new tasks created.`);
            fetchUserTasks();
        } catch (err) {
            setUploadError(err.message || 'An unexpected error occurred.');
        } finally {
            setIsProcessing(false);
            setFile(null);
            e.target.reset();
        }
    };

    return (
         <>
            <div className="card process-card">
                <h2>Process New Meeting</h2>
                <form onSubmit={handleFileUpload}>
                    <div className="file-input-wrapper">
                        <input type="file" id="audio-file" onChange={(e) => setFile(e.target.files[0])} accept="audio/*" disabled={isProcessing} />
                        <label htmlFor="audio-file" className="file-input-label">{file ? file.name : 'Choose an audio file...'}</label>
                    </div>
                    <button type="submit" className="process-button" disabled={!file || isProcessing}>{isProcessing ? 'Processing...' : 'Upload & Analyze'}</button>
                </form>
                {uploadError && <p className="error-message upload-status">{uploadError}</p>}
                {processResult && <p className="success-message upload-status">{processResult}</p>}
            </div>
            <div className="card tasks-card">
                <h2>My Action Items</h2>
                {error && <p className="error-message">{error}</p>}
                {isLoadingTasks ? (<p>Loading tasks...</p>) : (
                    <div className="task-list">
                        {userTasks.length > 0 ? (
                            userTasks.map(task => <UserTaskItem key={task.id} task={task} />)
                        ) : (<p className="no-tasks-message">You have no pending tasks.</p>)}
                    </div>
                )}
            </div>
        </>
    );
};


//=========== Main App Component ===========//
function App() {
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!token) {
        setIsLoading(false);
        return;
    }
    const fetchUserData = async () => {
      try {
        const userData = await apiClient.request('/users/me', { token });
        setUser(userData);
      } catch (err) {
         console.error("Auth token is invalid, logging out.");
         handleLogout();
      } finally {
        setIsLoading(false);
      }
    };
    fetchUserData();
  }, [token]);
  
  const handleLogin = (newToken) => {
    localStorage.setItem('authToken', newToken);
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    setToken(null);
    setUser(null);
  };
  
  if (isLoading) {
    return <div className="loading-container"><p>Loading...</p></div>;
  }

  return (
    <div className="app-container">
      {!token || !user ? (
        <LoginPage onLogin={handleLogin} />
      ) : (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <h1>Welcome, {user.username}! {user.is_admin && '(Admin)'}</h1>
                <button onClick={handleLogout} className="logout-button">Logout</button>
            </header>
            <main className={`dashboard-main ${user.is_admin ? 'admin-layout' : ''}`}>
                {user.is_admin ? <AdminDashboard token={token} /> : <UserDashboard token={token} user={user} />}
            </main>
        </div>
      )}
    </div>
  );
}

export default App;