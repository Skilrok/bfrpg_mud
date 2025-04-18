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
    
    // Process command (placeholder - would connect to backend API)
    function processCommand(command) {
        // Log command to feedback area
        const commandFeedback = document.querySelector('.command-feedback');
        const commandDiv = document.createElement('div');
        commandDiv.className = 'command';
        commandDiv.textContent = '> ' + command;
        
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'feedback';
        
        // Handle some basic commands for demo purposes
        if (command.toLowerCase() === 'help') {
            feedbackDiv.textContent = 'Available commands: look, inventory, help, read journal';
        } else if (command.toLowerCase() === 'read journal' || command.toLowerCase() === 'journal') {
            feedbackDiv.textContent = 'Opening your journal...';
            toggleJournal();
        } else if (command.toLowerCase().startsWith('look')) {
            feedbackDiv.textContent = 'You see nothing unusual.';
        } else if (command.toLowerCase() === 'inventory') {
            feedbackDiv.textContent = 'You are carrying: a backpack, rations, a torch, and a rusty dagger.';
        } else {
            feedbackDiv.textContent = 'Command not recognized. Type "help" for assistance.';
        }
        
        // Clear old feedback and add new
        commandFeedback.innerHTML = '';
        commandFeedback.appendChild(commandDiv);
        commandFeedback.appendChild(feedbackDiv);
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
    
    // Future WebSocket connection for real-time updates
    function connectWebSocket() {
        // WebSocket implementation would go here
        console.log('WebSocket connection would be established here');
    }
}); 