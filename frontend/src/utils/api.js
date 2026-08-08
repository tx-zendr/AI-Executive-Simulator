export const fetchSimulation = async (productData) => {
    try {
        const response = await fetch("http://127.0.0.1:5173/simulate", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ idea: productData.description })
        });
        
        if (!response.ok) throw new Error('Simulation failed');
        return await response.json();
    } catch (error) {
        console.error("API Error:", error);
        return null;
    }
};

export const fetchThreads = async () => {
    try {
        const response = await fetch("http://127.0.0.1:5173/threads");
        if (!response.ok) throw new Error('Failed to fetch threads');
        return await response.json(); 
    } catch (error) {
        console.error("API Error - Server Offline:", error);
        return [];
    }
};

export const fetchThreadHistory = async (thread_id) => {
    try {
        const response = await fetch(`http://127.0.0.1:5173/history/${thread_id}`);
        if (!response.ok) throw new Error('Failed to fetch history');
        return await response.json();
    } catch (error) {
        console.error("API Error:", error);
        return null;
    }
};