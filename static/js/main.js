// BFRPG MUD UI JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const commandInput = document.querySelector('.command-input');
    const journal = document.querySelector('.journal');
    
    // Command history
    const commandHistory = [];
    let currentHistoryIndex = -1;
    
    // Command input handling
    commandInput.addEventListener('keydown', function(e) {
        // Handle Enter key (send command)
        if (e.key === 'Enter') {
            const command = commandInput.value.trim();
            if (command) {
                processCommand(command);
                commandHistory.unshift(command);
                currentHistoryIndex = -1;
                commandInput.value = '';
            }
            e.preventDefault();
        }
        
        // Handle Up arrow (navigate command history)
        else if (e.key === 'ArrowUp') {
            if (commandHistory.length > 0 && currentHistoryIndex < commandHistory.length - 1) {
                currentHistoryIndex++;
                commandInput.value = commandHistory[currentHistoryIndex];
                // Move cursor to end of input
                setTimeout(() => {
                    commandInput.selectionStart = commandInput.selectionEnd = commandInput.value.length;
                }, 0);
            }
            e.preventDefault();
        }
        
        // Handle Down arrow (navigate command history)
        else if (e.key === 'ArrowDown') {
            if (currentHistoryIndex > 0) {
                currentHistoryIndex--;
                commandInput.value = commandHistory[currentHistoryIndex];
            } else if (currentHistoryIndex === 0) {
                currentHistoryIndex = -1;
                commandInput.value = '';
            }
            e.preventDefault();
        }
        
        // Handle Tab key (autocomplete) - placeholder for future implementation
        else if (e.key === 'Tab') {
            // Autocomplete logic would go here
            e.preventDefault();
        }
    });
    
    // Process command (connects to backend API)
    async function processCommand(command) {
        // Log command to feedback area
        const commandFeedback = document.querySelector('.command-feedback');
        const commandDiv = document.createElement('div');
        commandDiv.className = 'command';
        commandDiv.textContent = '> ' + command;
        commandFeedback.appendChild(commandDiv);
        
        try {
            // Get token from localStorage
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Not authenticated. Please login first.');
            }
            
            // Get active character ID
            const activeCharacter = JSON.parse(localStorage.getItem('activeCharacter') || '{}');
            const characterId = activeCharacter.id;
            
            // Send command to API
            const response = await fetch('/api/commands', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    command: command,
                    character_id: characterId
                })
            });
            
            if (!response.ok) {
                // Handle HTTP error
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error processing command');
            }
            
            // Parse response
            const data = await response.json();
            
            // Create feedback element
            const feedbackDiv = document.createElement('div');
            feedbackDiv.className = 'feedback';
            
            if (data.success) {
                feedbackDiv.textContent = data.message;
                
                // Handle special data if needed
                if (data.data) {
                    // For future special rendering based on command type
                    console.log('Command data:', data.data);
                }
            } else {
                // Command failed
                feedbackDiv.textContent = data.message || 'Command failed.';
                feedbackDiv.classList.add('error');
            }
            
            // Add feedback to the command area
            commandFeedback.appendChild(feedbackDiv);
            
        } catch (error) {
            // Handle any errors
            const feedbackDiv = document.createElement('div');
            feedbackDiv.className = 'feedback error';
            feedbackDiv.textContent = error.message || 'An error occurred.';
            commandFeedback.appendChild(feedbackDiv);
        }
        
        // Scroll to bottom of feedback area
        commandFeedback.scrollTop = commandFeedback.scrollHeight;
    }
    
    // Toggle journal visibility
    function toggleJournal() {
        journal.classList.toggle('hidden');
    }
    
    // Focus command input when clicking anywhere in the terminal
    document.querySelector('.terminal').addEventListener('click', function() {
        commandInput.focus();
    });
    
    // Initialize
    commandInput.focus();
    
    // Initialize WebSocket connection
    if (document.querySelector('.game-interface')) {
        // Only connect if we're on the game interface page
        connectWebSocket();
    }
    
    // WebSocket connection for real-time updates
    function connectWebSocket() {
        const token = localStorage.getItem('token');
        if (!token) {
            console.error('Cannot establish WebSocket: No authentication token');
            return;
        }
        
        const activeCharacter = JSON.parse(localStorage.getItem('activeCharacter') || '{}');
        const characterId = activeCharacter.id;
        
        // Establish WebSocket connection
        const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const wsUrl = `${protocol}${window.location.host}/api/commands/ws`;
        
        const socket = new WebSocket(wsUrl);
        
        socket.onopen = function(e) {
            console.log('WebSocket connection established');
            
            // Send authentication message
            socket.send(JSON.stringify({
                type: 'auth',
                token: token,
                character_id: characterId
            }));
        };
        
        socket.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                
                // Handle command responses
                if (data.command) {
                    // Only handle if we didn't initiate the command (for events, broadcasts, etc.)
                    if (!data.source || data.source !== 'self') {
                        const commandFeedback = document.querySelector('.command-feedback');
                        
                        // Create feedback element
                        const feedbackDiv = document.createElement('div');
                        feedbackDiv.className = data.success ? 'feedback server' : 'feedback error server';
                        feedbackDiv.textContent = data.message;
                        
                        // Add to the command area
                        commandFeedback.appendChild(feedbackDiv);
                        
                        // Scroll to bottom
                        commandFeedback.scrollTop = commandFeedback.scrollHeight;
                    }
                }
                
                // Handle room updates, character updates, etc.
                if (data.type === 'room_update') {
                    // Update display for room changes
                    console.log('Room update:', data);
                } else if (data.type === 'character_update') {
                    // Update character stats display
                    console.log('Character update:', data);
                }
                
            } catch (e) {
                console.error('Error parsing WebSocket message:', e);
            }
        };
        
        socket.onclose = function(event) {
            if (event.wasClean) {
                console.log(`WebSocket connection closed cleanly, code=${event.code} reason=${event.reason}`);
            } else {
                // Connection died
                console.error('WebSocket connection died');
                
                // Try to reconnect after a delay
                setTimeout(connectWebSocket, 5000);
            }
        };
        
        socket.onerror = function(error) {
            console.error(`WebSocket error: ${error.message}`);
        };
        
        // Store socket reference
        window.gameSocket = socket;
        
        return socket;
    }
}); 