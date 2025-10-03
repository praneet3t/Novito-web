import React, { useState, useEffect, useCallback } from 'react';

//=========== API Client ===========//
const apiClient = {
  async request(endpoint, { body, token, method = 'GET', ...customConfig }) {
    const headers = {};
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    const config = { method, ...customConfig, headers: { ...headers, ...customConfig.headers } };
    if (body) {
      if (body instanceof FormData) {
        config.body = body; // Don't set Content-Type for FormData, browser does it
      } else {
        config.headers['Content-Type'] = 'application/json';
        config.body = JSON.stringify(body);
      }
    }
    const response = await fetch(`http://127.0.0.1:8000${endpoint}`, config);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      return Promise.reject(errorData);
    }
    if (response.status !== 204) return response.json();
  },
};

//=========== Login Page Component ===========//
function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('Admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    const formData = new URLSearchParams({ username, password });
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
      <div className="card">
        <h1 className="auth-title">Meeting Agent</h1>
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
            <p><strong>Log in as:</strong> Admin (admin123) or Priya (priya123)</p>
        </div>
      </div>
    </div>
  );
}

//=========== User Dashboard Component ===========//
function UserDashboard({ token }) {
    const [tasks, setTasks] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        apiClient.request('/users/me/tasks', { token })
            .then(setTasks)
            .finally(() => setIsLoading(false));
    }, [token]);

    if (isLoading) return <div className="card"><p>Loading your tasks...</p></div>;

    return (
        <div className="card tasks-card">
            <h2>My Action Items</h2>
            {tasks.length > 0 ? (
                <div className="task-list">
                    {tasks.map(task => (
                        <div className="task-item" key={task.id}>
                            <span className={`status-indicator status-${task.status.toLowerCase().replace(' ', '-')}`}></span>
                            <div className="task-details">
                                <p className="task-description">{task.description}</p>
                                {task.due_date && <p className="task-due-date">Due: {task.due_date}</p>}
                            </div>
                            <span className="task-status">{task.status}</span>
                        </div>
                    ))}
                </div>
            ) : (
                <p className="no-tasks-message">You have no pending tasks. Great job!</p>
            )}
        </div>
    );
}

//=========== Admin Dashboard Component ===========//
function AdminDashboard({ token }) {
    const [stats, setStats] = useState(null);
    const [tasks, setTasks] = useState([]);
    const [isLoadingTasks, setIsLoadingTasks] = useState(true);

    // Form State
    const [title, setTitle] = useState('');
    const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
    const [uploadType, setUploadType] = useState('audio');
    const [transcript, setTranscript] = useState('');
    const [audioFile, setAudioFile] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const fetchAllData = useCallback(() => {
        setIsLoadingTasks(true);
        apiClient.request('/admin/stats', { token }).then(setStats);
        apiClient.request('/admin/tasks', { token }).then(setTasks).finally(() => setIsLoadingTasks(false));
    }, [token]);

    useEffect(fetchAllData, [fetchAllData]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsProcessing(true);
        setError('');
        setSuccess('');

        const formData = new FormData();
        formData.append('title', title);
        formData.append('date', date);

        if (uploadType === 'audio' && audioFile) {
            formData.append('audio_file', audioFile);
        } else if (uploadType === 'transcript' && transcript) {
            formData.append('transcript', transcript);
        } else {
            setError('Please provide either an audio file or a transcript.');
            setIsProcessing(false);
            return;
        }

        try {
            const result = await apiClient.request('/admin/process-meeting/', { method: 'POST', token, body: formData });
            setSuccess(`Meeting processed! Created ${result.created_tasks} new tasks.`);
            setTitle(''); setDate(new Date().toISOString().split('T')[0]); setTranscript(''); setAudioFile(null);
            e.target.reset(); // Reset the form fields
            fetchAllData();
        } catch (err) {
            setError(err.detail || 'Failed to process meeting.');
        } finally {
            setIsProcessing(false);
        }
    };
    
    return (
        <div className="admin-dashboard-grid">
            {stats && (
                <div className="stats-grid">
                    <div className="card stat-card"><div className="stat-value">{stats.total_meetings}</div><div className="stat-label">Meetings</div></div>
                    <div className="card stat-card"><div className="stat-value">{stats.total_tasks}</div><div className="stat-label">Total Tasks</div></div>
                    <div className="card stat-card"><div className="stat-value">{stats.tasks_todo}</div><div className="stat-label">Pending</div></div>
                    <div className="card stat-card"><div className="stat-value">{stats.tasks_completed}</div><div className="stat-label">Completed</div></div>
                </div>
            )}
            
            <div className="card">
                <h2>Process New Meeting</h2>
                <form onSubmit={handleSubmit}>
                    <div className="form-grid">
                        <div className="input-group">
                            <label htmlFor="title">Meeting Title</label>
                            <input type="text" id="title" value={title} onChange={(e) => setTitle(e.target.value)} required/>
                        </div>
                        <div className="input-group">
                            <label htmlFor="date">Meeting Date</label>
                            <input type="date" id="date" value={date} onChange={(e) => setDate(e.target.value)} required/>
                        </div>
                    </div>
                    <div className="upload-toggle">
                        <button type="button" onClick={() => setUploadType('audio')} className={`toggle-button ${uploadType === 'audio' ? 'active' : ''}`}>Upload Audio</button>
                        <button type="button" onClick={() => setUploadType('transcript')} className={`toggle-button ${uploadType === 'transcript' ? 'active' : ''}`}>Paste Transcript</button>
                    </div>

                    {uploadType === 'audio' ? (
                        <div className="input-group">
                            <label htmlFor="audio-file" className="file-input-label">{audioFile ? audioFile.name : 'Click to select an audio file'}</label>
                            <input type="file" id="audio-file" onChange={(e) => setAudioFile(e.target.files[0])} accept="audio/*"/>
                        </div>
                    ) : (
                        <div className="input-group">
                             <textarea value={transcript} onChange={(e) => setTranscript(e.target.value)} placeholder="Paste the full meeting transcript here..."></textarea>
                        </div>
                    )}
                    
                    {error && <p className="error-message">{error}</p>}
                    {success && <p className="success-message">{success}</p>}
                    
                    <button type="submit" className="auth-button full-width" disabled={isProcessing}>{isProcessing ? 'Processing...' : 'Process Meeting'}</button>
                </form>
            </div>
        </div>
    );
}


//=========== Main App Component ===========//
function App() {
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    setToken(null);
    setUser(null);
  };

  useEffect(() => {
    if (!token) {
        setIsLoading(false);
        return;
    }
    apiClient.request('/users/me', { token })
        .then(setUser)
        .catch(() => handleLogout()) // Log out if token is invalid
        .finally(() => setIsLoading(false));
  }, [token]);
  
  const handleLogin = (newToken) => {
    localStorage.setItem('authToken', newToken);
    setToken(newToken);
  };
  
  if (isLoading) return <div className="loading-container"><p>Loading...</p></div>;

  return (
    <div className="app-container">
      {!token || !user ? (
        <LoginPage onLogin={handleLogin} />
      ) : (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <h1>Welcome, {user.username}! {user.is_admin && <span style={{color: 'var(--primary-color)'}}>(Admin)</span>}</h1>
                <button onClick={handleLogout} className="logout-button">Logout</button>
            </header>
            <main className="dashboard-main">
                {user.is_admin ? <AdminDashboard token={token} /> : <UserDashboard token={token} />}
            </main>
        </div>
      )}
    </div>
  );
}

export default App;