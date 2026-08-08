import React, { useEffect, useState } from 'react'
import { fetchThreads } from '../utils/api'
import './HistorySidebar.css'

const HistorySidebar = ({ isOpen, onClose, onLoadHistory }) => {
    const [threads, setThreads] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    useEffect(() => {
        if (isOpen) {
            setIsLoading(true);
            fetchThreads().then(data => {
                setThreads(data);
                setIsLoading(false);
            });
        }
    }, [isOpen]);

    return (
        <>
            {isOpen && <div className="sidebar-overlay" onClick={onClose}></div>}
            
            <div className={`history-sidebar ${isOpen ? 'open' : ''}`}>
                <div className="sidebar-header">
                    <h2>Session History</h2>
                    <button className="close-btn" onClick={onClose}>×</button>
                </div>

                <div className="thread-list">
                    {isLoading ? (
                        <div className="thread-loading">Retrieving archives...</div>
                    ) : threads.length > 0 ? (
                        threads.map((thread, idx) => (
                            <div 
                                key={idx} 
                                className="thread-item"
                                onClick={() => onLoadHistory(thread.thread_id)}
                            >
                                <div className="thread-icon"></div>
                                <div className="thread-name">{thread.name || thread.thread_id}</div>
                            </div>
                        ))
                    ) : (
                        <div className="thread-loading">No history found.</div>
                    )}
                </div>
            </div>
        </>
    )
}

export default HistorySidebar