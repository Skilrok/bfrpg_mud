/**
 * Game Interface JavaScript
 * Handles the terminal-style game interface with command processing,
 * character data loading, and UI updates.
 */

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const gameOutput = document.querySelector('.game-output');
    const commandInput = document.getElementById('command-input');
    const usernameDisplay = document.getElementById('username');
    const logoutBtn = document.getElementById('logout-btn');
    const charName = document.getElementById('char-name');
    const charClass = document.getElementById('char-class');
    const charClassDetail = document.getElementById('char-class-detail');
    const charLevel = document.getElementById('char-level');
    const charHp = document.getElementById('char-hp');
    const charHpDetail = document.getElementById('char-hp-detail');
    const charRace = document.getElementById('char-race');
    const charStr = document.getElementById('char-str');
    const charInt = document.getElementById('char-int');
    const charWis = document.getElementById('char-wis');
    const charDex = document.getElementById('char-dex');
    const charCon = document.getElementById('char-con');
    const charCha = document.getElementById('char-cha');
    const equipmentList = document.getElementById('equipment-list');
    const journalContent = document.getElementById('journal-content');
    const journalInput = document.getElementById('journal-input');
    const characterSelectionModal = document.getElementById('character-selection-modal');
    const characterListContainer = document.getElementById('character-list');
    const createCharacterBtn = document.getElementById('create-character-btn');
    const partyMembers = document.getElementById('party-members');

    // Authentication state
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');
    let characterId = localStorage.getItem('characterId');

    // Redirect to login if not authenticated
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    // Set username display
    usernameDisplay.textContent = username || 'Unknown';

    // Logout function
    logoutBtn.addEventListener('click', function() {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        localStorage.removeItem('characterId');
        window.location.href = 'login.html';
    });

    // Journal entry handling
    if (journalInput) {
        journalInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' && this.value.trim() !== '') {
                const date = new Date();
                const formattedDate = `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
                
                addJournalEntry({
                    date: formattedDate,
                    text: this.value.trim()
                });
                
                // Save journal entry to API (if implemented)
                // saveJournalEntry(characterId, this.value.trim());
                
                this.value = '';
            }
        });
    }

    // Create new character button
    let createCharPending = false;
    createCharacterBtn.addEventListener('click', function() {
        // Prevent multiple clicks
        if (createCharPending) return;
        
        createCharPending = true;
        
        // Send a command to begin character creation
        sendCommand('create character New Character');
        hideCharacterSelectionModal();
        
        // Reset after a delay
        setTimeout(() => {
            createCharPending = false;
        }, 1000);
    });

    // Game state
    let gameHistory = [];
    let historyIndex = -1;
    let wsConnection = null;
    let useWebSocket = true;
    let sessionId = generateSessionId();
    let characters = [];
    let selectedCharacterId = null;
    let partyData = []; // Store party members (character + hirelings)

    // Variables for command debouncing
    let lastCommand = '';
    let lastCommandTime = 0;
    const COMMAND_DEBOUNCE_MS = 500; // 500ms debounce time

    // Initialize game
    function initGame() {
        // Clear any leftover modal display state
        if (characterSelectionModal) {
            characterSelectionModal.style.display = 'none';
        }
        
        // Check URL parameters first (they override localStorage)
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('char')) {
            const urlCharId = urlParams.get('char');
            console.log("Found character ID in URL:", urlCharId);
            if (urlCharId) {
                // Set to localStorage and use this
                localStorage.setItem('characterId', urlCharId);
                characterId = urlCharId;
            }
        }
        
        // Check if we have a character ID
        if (characterId) {
            console.log("Using character ID:", characterId);
            // Try to load the character data
            loadCharacterData(characterId)
                .then(success => {
                    if (success) {
                        displayMessage("Welcome to Basic Fantasy RPG MUD!", "system");
                        displayMessage("Type 'help' for a list of commands.", "system");
                        // Load party members (hirelings) if available
                        loadPartyMembers(characterId);
                    } else {
                        console.error("Failed to load character data for ID:", characterId);
                        // Clear invalid character ID
                        localStorage.removeItem('characterId');
                        characterId = null;
                        // Display error message but don't auto-show character selection
                        displayMessage("Error loading character data. Type 'characters' to select a character.", "error");
                    }
                })
                .catch(error => {
                    console.error("Error loading character:", error);
                    // Clear invalid character ID
                    localStorage.removeItem('characterId');
                    characterId = null;
                    // Display error message but don't auto-show character selection
                    displayMessage("Error loading character data. Type 'characters' to select a character.", "error");
                });
        } else {
            // Show welcome message first
            displayMessage("Welcome to Basic Fantasy RPG MUD!", "system");
            displayMessage("You need to select a character to play. Opening character selection...", "system");
            displayMessage("Type 'characters' if you need to reopen the character selection screen.", "system");
            
            // Use timeout to show character selection after messages
            setTimeout(() => {
                showCharacterSelection();
            }, 500);
        }

        // Try to establish WebSocket connection
        if (useWebSocket) {
            connectWebSocket();
        }

        // Focus the input field
        commandInput.focus();
    }

    // Show character selection modal
    function showCharacterSelection() {
        // Load characters for the user
        loadCharacters()
            .then(chars => {
                characters = chars;
                renderCharacterList();
                characterSelectionModal.classList.add('active');
                characterSelectionModal.style.display = 'block';

                // Add event listener for clicking outside the modal content
                characterSelectionModal.addEventListener('click', function(event) {
                    // If the click is directly on the modal background (not its children)
                    if (event.target === characterSelectionModal) {
                        hideCharacterSelectionModal();
                    }
                });
            })
            .catch(error => {
                console.error("Error loading characters:", error);
                displayMessage("Error loading characters. Please try again later.", "error");
            });
    }

    // Hide character selection modal
    function hideCharacterSelectionModal() {
        characterSelectionModal.classList.remove('active');
        characterSelectionModal.style.display = 'none';
        console.log("Character selection modal hidden");
    }

    // Load characters for the current user
    async function loadCharacters() {
        try {
            const response = await fetch('/api/characters', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const characters = await response.json();
            return characters;
        } catch (error) {
            console.error("Error loading characters:", error);
            throw error;
        }
    }

    // Render the character list in the selection modal
    function renderCharacterList() {
        characterListContainer.innerHTML = '';

        // Add close button to the modal if it doesn't exist already
        const modalHeader = characterListContainer.parentElement.querySelector('.modal-header');
        if (modalHeader && !modalHeader.querySelector('.close-modal-btn')) {
            const closeButton = document.createElement('button');
            closeButton.classList.add('close-modal-btn');
            closeButton.innerHTML = '&times;';
            closeButton.addEventListener('click', hideCharacterSelectionModal);
            modalHeader.appendChild(closeButton);
        }

        if (characters.length === 0) {
            characterListContainer.innerHTML = `
                <div class="loading-message">
                    No characters found. Click "Create New Character" to get started.
                </div>
            `;
            return;
        }

        characters.forEach(character => {
            const card = document.createElement('div');
            card.classList.add('character-card');
            if (character.id === selectedCharacterId) {
                card.classList.add('selected');
            }

            card.innerHTML = `
                <h3>${character.name}</h3>
                <div class="character-info">
                    <div class="character-info-left">
                        <div class="character-stat">Race: ${character.race}</div>
                        <div class="character-stat">Class: ${character.character_class}</div>
                        <div class="character-stat">Level: ${character.level}</div>
                    </div>
                    <div class="character-info-right">
                        <div class="character-stat">HP: ${character.hit_points}</div>
                        <div class="character-stat">Gold: ${character.gold}</div>
                    </div>
                </div>
                <div class="character-card-actions">
                    <button class="btn select-btn" data-id="${character.id}">Select Character</button>
                </div>
            `;

            characterListContainer.appendChild(card);
        });
        
        // Attach event listeners to select buttons
        document.querySelectorAll('.select-btn').forEach((btn) => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent the card click from firing
                const charId = btn.getAttribute('data-id');
                if (charId) {
                    selectCharacter(charId);
                }
            });
        });
    }

    // Select a character and start the game
    function selectCharacter(id) {
        // Ensure id is treated as a string (it might come as a number from API)
        id = String(id);
        
        // Set character state
        selectedCharacterId = id;
        characterId = id;
        localStorage.setItem('characterId', id);
        
        console.log("Character selected:", id);

        // Find character info in our list
        const selectedCharacter = characters.find(c => String(c.id) === id);
        
        // First hide the modal immediately to provide user feedback
        if (characterSelectionModal) {
            hideCharacterSelectionModal();
        }

        // Load the character data
        loadCharacterData(id)
            .then(success => {
                if (success) {
                    if (selectedCharacter) {
                        displayMessage(`Character selected: ${selectedCharacter.name}`, "system");
                    } else {
                        displayMessage("Character selected successfully", "system");
                    }
                    displayMessage("Type 'look' to see your surroundings.", "system");
                    
                    // Load party members
                    loadPartyMembers(id);
                } else {
                    displayMessage("Failed to load character data. Please try again.", "error");
                    // Don't reopen the modal, let the user decide if they want to try again
                }
            })
            .catch(error => {
                console.error("Error loading character:", error);
                displayMessage("Error loading character data. Please try again.", "error");
                // Don't reopen the modal, let the user decide if they want to try again
            });
    }

    // Make sure selectCharacter is available globally for the inline script
    window.selectCharacter = selectCharacter;

    // Load party members (character + hirelings)
    async function loadPartyMembers(characterId) {
        try {
            // Load hirelings if the API endpoint exists
            const response = await fetch(`/api/characters/${characterId}/hirelings`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const hirelings = await response.json();
                // Add hirelings to the party data
                partyData = hirelings;
                updatePartyDisplay();
            } else if (response.status !== 404) {
                // Log the error only if it's not a 404 (endpoint might not exist yet)
                console.error("Error loading hirelings:", response.statusText);
            }
        } catch (error) {
            console.error("Error loading party members:", error);
        }
    }

    // Update the party display with character and hirelings
    function updatePartyDisplay() {
        // If partyMembers element doesn't exist, return
        if (!partyMembers) return;

        // Keep the main character at the top
        // Other party members will be added/updated dynamically
        const mainCharacterHtml = `
            <div class="party-member">
                <div class="party-member-name" id="char-name">${charName.textContent}</div>
                <div class="party-member-info">
                    <div id="char-class">${charClassDetail.textContent}</div>
                    <div id="char-hp">${charHpDetail.textContent}</div>
                </div>
            </div>
        `;

        // Start with the main character
        let partyHtml = mainCharacterHtml;

        // Add all hirelings
        if (partyData.length > 0) {
            partyData.forEach(hireling => {
                partyHtml += `
                    <div class="party-member">
                        <div class="party-member-name">${hireling.name}</div>
                        <div class="party-member-info">
                            <div>Class: ${hireling.character_class || 'Unknown'}</div>
                            <div>HP: ${hireling.hit_points || '?'}/${hireling.max_hit_points || '?'}</div>
                        </div>
                    </div>
                `;
            });
        } else {
            // Add placeholder hirelings for demonstration if no hirelings exist
            partyHtml += `
                <div class="party-member">
                    <div class="party-member-name">No hirelings</div>
                    <div class="party-member-info">
                        <div>Hire companions to join your party</div>
                    </div>
                </div>
            `;
        }

        // Update the party display
        partyMembers.innerHTML = partyHtml;
    }

    // Generate a unique session ID
    function generateSessionId() {
        return 'session_' + Math.random().toString(36).substring(2, 15) +
               Math.random().toString(36).substring(2, 15);
    }

    // Connect to WebSocket for commands
    function connectWebSocket() {
        // Check if browser supports WebSocket
        if (!window.WebSocket) {
            useWebSocket = false;
            displayMessage("Your browser doesn't support WebSockets. Falling back to HTTP.", "system");
            return;
        }

        // Make sure we have a fresh token
        const currentToken = localStorage.getItem('token');
        if (!currentToken) {
            displayMessage("Authentication required. Please log in again.", "error");
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
            return;
        }

        // Create WebSocket connection
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/commands`;

        try {
            // Close existing connection if any
            if (wsConnection && wsConnection.readyState !== WebSocket.CLOSED) {
                wsConnection.close();
            }
            
            wsConnection = new WebSocket(wsUrl);

            // Connection opened
            wsConnection.onopen = function() {
                // Send authentication data
                wsConnection.send(JSON.stringify({
                    token: currentToken,
                    character_id: characterId,
                    session_id: sessionId
                }));
                displayMessage("WebSocket connected.", "system");
            };

            // Listen for messages
            wsConnection.onmessage = function(event) {
                const data = JSON.parse(event.data);

                if (data.message) {
                    if (!data.success) {
                        // Handle error messages
                        displayMessage(data.message, "error");
                        
                        // If token is invalid, redirect to login
                        if (data.message.includes("Invalid or expired token")) {
                            displayMessage("Session expired. Please log in again.", "error");
                            setTimeout(() => {
                                localStorage.removeItem('token');
                                window.location.href = 'login.html';
                            }, 2000);
                        }
                    } else {
                        // Regular success messages
                        displayMessage(data.message, "normal");
                    }
                }

                // Update character info if provided
                if (data.data && data.data.character) {
                    updateCharacterInfo(data.data.character);
                }

                // Update inventory if provided
                if (data.data && data.data.inventory) {
                    updateInventory(data.data.inventory);
                }

                // Update journal if provided
                if (data.data && data.data.journal) {
                    addJournalEntry(data.data.journal);
                }
            };

            // Connection error
            wsConnection.onerror = function(error) {
                console.error("WebSocket error:", error);
                displayMessage("WebSocket connection error. Trying to reconnect...", "error");
                setTimeout(connectWebSocket, 3000);
            };

            // Connection closed
            wsConnection.onclose = function(event) {
                const reason = event.reason || "Unknown reason";
                displayMessage(`WebSocket connection closed. Code=${event.code} reason=${reason}`, "system");
                
                // Try to reconnect unless it was a clean close (1000) or authentication issue (4000-4099)
                if (event.code !== 1000 && (event.code < 4000 || event.code > 4099)) {
                    displayMessage("Attempting to reconnect in 3 seconds...", "system");
                    setTimeout(connectWebSocket, 3000);
                } else if (event.code >= 4000 && event.code <= 4099) {
                    // Authentication issue
                    displayMessage("Authentication error. Please log in again.", "error");
                    setTimeout(() => {
                        localStorage.removeItem('token');
                        window.location.href = 'login.html';
                    }, 2000);
                }
            };

        } catch (e) {
            displayMessage("Failed to connect to WebSocket. Using HTTP instead.", "error");
            useWebSocket = false;
        }
    }

    // Display a message in the game output
    function displayMessage(message, type = "normal") {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');

        if (type === "system") {
            messageElement.classList.add('system-message');
            messageElement.innerHTML = `<span class="system-prefix">[SYSTEM]:</span> ${message}`;
        } else if (type === "error") {
            messageElement.classList.add('error-message');
            messageElement.innerHTML = `<span class="error-prefix">[ERROR]:</span> ${message}`;
        } else if (type === "command") {
            messageElement.classList.add('command-message');
            messageElement.innerHTML = `<span class="command-prefix">></span> ${message}`;
        } else {
            messageElement.textContent = message;
        }

        gameOutput.appendChild(messageElement);
        gameOutput.scrollTop = gameOutput.scrollHeight; // Auto-scroll to bottom
    }

    // Send a command to the server
    async function sendCommand(command) {
        // Debounce to prevent duplicate rapid command submissions
        const now = Date.now();
        if (command === lastCommand && now - lastCommandTime < COMMAND_DEBOUNCE_MS) {
            console.log("Command debounced:", command);
            return;
        }
        
        // Update debounce tracking
        lastCommand = command;
        lastCommandTime = now;
        
        // Add command to history
        gameHistory.push(command);
        historyIndex = gameHistory.length;

        // Special client-side commands
        const commandLower = command.trim().toLowerCase();
        
        if (commandLower === "characters") {
            displayMessage("Opening character selection...", "system");
            showCharacterSelection();
            commandInput.value = '';
            return;
        }
        
        if (commandLower.startsWith("select ")) {
            const characterName = command.trim().substring(7);
            if (characterName) {
                selectCharacterByName(characterName);
                commandInput.value = '';
                return;
            }
        }

        // Display the command
        displayMessage(command, "command");

        // If using WebSockets and connected, send via WS
        if (useWebSocket && wsConnection && wsConnection.readyState === WebSocket.OPEN) {
            wsConnection.send(JSON.stringify({
                command: command
            }));
            // Clear input after sending
            commandInput.value = '';
            return;
        }

        // Otherwise, fall back to HTTP API
        const currentToken = localStorage.getItem('token');
        if (!currentToken) {
            displayMessage("Authentication required. Please log in again.", "error");
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
            return;
        }
        
        try {
            // Construct headers with current token
            const headers = {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            };

            // Prepare the body
            const body = {
                command: command,
                character_id: characterId,
                session_id: sessionId
            };

            const response = await fetch('/api/commands', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(body)
            });

            const data = await response.json();

            if (data.message) {
                if (!data.success) {
                    displayMessage(data.message, "error");
                    
                    // Check if we need to show character selection
                    if (data.message.includes("need to select or create a character") ||
                        data.message.includes("No active character")) {
                        showCharacterSelection();
                    }
                } else {
                    displayMessage(data.message);
                }
            }

            // Update character info if provided
            if (data.data && data.data.character) {
                updateCharacterInfo(data.data.character);
            }

            // Update inventory if provided
            if (data.data && data.data.inventory) {
                updateInventory(data.data.inventory);
            }

            // Update journal if provided
            if (data.data && data.data.journal) {
                addJournalEntry(data.data.journal);
            }

        } catch (error) {
            console.error('Error:', error);
            displayMessage('Failed to send command. Server may be down.', "error");

            // Try to reconnect WebSocket on next command
            if (useWebSocket) {
                connectWebSocket();
            }
        }
    }

    // Expose sendCommand globally for inline scripts
    window.sendCommand = sendCommand;

    // Update character information
    function updateCharacterInfo(character) {
        if (!character) return;

        // Update main character display
        if (charName) charName.textContent = character.name || 'Unknown Character';
        
        // Update detailed character sheet
        // Basic character information
        const characterClassLevel = `${character.character_class || 'Unknown'} ${character.level || 1}`;
        document.getElementById('char-class-level').textContent = characterClassLevel;
        document.getElementById('char-race').textContent = character.race || 'Unknown';
        
        // Ability scores
        updateAbilityScore('char-str', character.strength || 10);
        updateAbilityScore('char-dex', character.dexterity || 10);
        updateAbilityScore('char-con', character.constitution || 10);
        updateAbilityScore('char-int', character.intelligence || 10);
        updateAbilityScore('char-wis', character.wisdom || 10);
        updateAbilityScore('char-cha', character.charisma || 10);
        
        // Combat stats
        document.getElementById('char-hp-detail').textContent = `${character.hit_points || 0}/${character.max_hit_points || character.hit_points || 0}`;
        document.getElementById('armor-class').textContent = character.armor_class || 10;
        document.getElementById('attack-bonus').textContent = character.attack_bonus || '+1';
        document.getElementById('initiative-mod').textContent = calculateModifier(character.dexterity || 10);
        document.getElementById('movement').textContent = character.movement || '40\'';
        document.getElementById('experience').textContent = `${character.experience || 0}/${getXPForNextLevel(character)}`;
        
        // Saving throws
        document.getElementById('save-death').textContent = character.save_death_ray_poison || 12;
        document.getElementById('save-wands').textContent = character.save_magic_wands || 13;
        document.getElementById('save-paralysis').textContent = character.save_paralysis_petrify || 14;
        document.getElementById('save-breath').textContent = character.save_dragon_breath || 15;
        document.getElementById('save-spells').textContent = character.save_spells || 16;
        
        // Class features
        updateClassFeatures(character);

        // Update equipment list
        updateInventory(character.equipment || []);
        
        // Update weapons
        updateWeapons(character.weapons || []);
        
        // Update party display
        updatePartyDisplay();
    }
    
    // Helper function to calculate ability modifier
    function calculateModifier(abilityScore) {
        const mod = Math.floor((abilityScore - 10) / 2);
        return mod >= 0 ? `+${mod}` : `${mod}`;
    }
    
    // Helper function to get XP needed for next level
    function getXPForNextLevel(character) {
        const level = character.level || 1;
        // Basic XP progression - customize based on your game rules
        const xpTable = [0, 2000, 4000, 8000, 16000, 32000, 64000, 120000, 240000, 360000];
        return xpTable[level] || xpTable[xpTable.length - 1];
    }
    
    // Update ability score and modifier
    function updateAbilityScore(elementId, score) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = score;
            // Also update the modifier
            const modId = `${elementId}-mod`;
            const modElement = document.getElementById(modId);
            if (modElement) {
                modElement.textContent = calculateModifier(score);
            }
        }
    }
    
    // Update class features based on character class
    function updateClassFeatures(character) {
        const featuresElement = document.getElementById('class-features');
        if (!featuresElement) return;
        
        const charClass = character.character_class || '';
        let featuresHTML = '';
        
        // Display class-specific features
        switch(charClass.toLowerCase()) {
            case 'cleric':
                featuresHTML = `
                    <div>Turn Undead</div>
                    <div>Spell Casting</div>
                    <div>Spells per day: ${getSpellsPerDay(character)}</div>
                `;
                break;
            case 'fighter':
                featuresHTML = `
                    <div>Combat Expertise</div>
                    <div>Bonus to-hit: ${calculateModifier(character.strength || 10)}</div>
                `;
                break;
            case 'magic-user':
                featuresHTML = `
                    <div>Spell Casting</div>
                    <div>Spells per day: ${getSpellsPerDay(character)}</div>
                    <div>Spells known: ${(character.spells_known || []).join(', ') || 'None'}</div>
                `;
                break;
            case 'thief':
                featuresHTML = createThiefSkillsHTML(character);
                break;
            default:
                featuresHTML = '<div>No special class features</div>';
        }
        
        featuresElement.innerHTML = featuresHTML;
    }
    
    // Get spells per day based on class and level
    function getSpellsPerDay(character) {
        const level = character.level || 1;
        const charClass = character.character_class || '';
        
        // Simple placeholder - you would replace with actual rules
        if (charClass.toLowerCase() === 'magic-user') {
            return level > 1 ? '2/1' : '1';
        } else if (charClass.toLowerCase() === 'cleric') {
            return level > 1 ? '1' : '0';
        }
        
        return '0';
    }
    
    // Create HTML for thief skills
    function createThiefSkillsHTML(character) {
        const thiefSkills = character.thief_abilities || {};
        return `
            <div class="thief-skills">
                <div class="skill"><span>Open Locks:</span> <span>${thiefSkills.open_locks || 15}%</span></div>
                <div class="skill"><span>Remove Traps:</span> <span>${thiefSkills.remove_traps || 10}%</span></div>
                <div class="skill"><span>Pick Pockets:</span> <span>${thiefSkills.pick_pockets || 20}%</span></div>
                <div class="skill"><span>Move Silently:</span> <span>${thiefSkills.move_silently || 20}%</span></div>
                <div class="skill"><span>Climb Walls:</span> <span>${thiefSkills.climb_walls || 85}%</span></div>
                <div class="skill"><span>Hide:</span> <span>${thiefSkills.hide || 10}%</span></div>
                <div class="skill"><span>Listen:</span> <span>${thiefSkills.listen || 30}%</span></div>
            </div>
        `;
    }
    
    // Update weapons table
    function updateWeapons(weapons) {
        const weaponsList = document.getElementById('weapons-list');
        if (!weaponsList) return;
        
        if (!weapons || weapons.length === 0) {
            weaponsList.innerHTML = `
                <tr>
                    <td colspan="4">No weapons</td>
                </tr>
            `;
            return;
        }
        
        let weaponsHTML = '';
        weapons.forEach(weapon => {
            if (typeof weapon === 'string') {
                // Simple weapon entry
                weaponsHTML += `
                    <tr>
                        <td>${weapon}</td>
                        <td>--</td>
                        <td>--</td>
                        <td>--</td>
                    </tr>
                `;
            } else {
                // Detailed weapon entry
                weaponsHTML += `
                    <tr>
                        <td>${weapon.name || 'Unknown'}</td>
                        <td>${weapon.attack || '--'}</td>
                        <td>${weapon.damage || '--'}</td>
                        <td>${weapon.notes || ''}</td>
                    </tr>
                `;
            }
        });
        
        weaponsList.innerHTML = weaponsHTML;
    }

    function updateInventory(inventoryItems) {
        if (!equipmentList) return;
        
        // Clear current equipment list
        equipmentList.innerHTML = '';
        
        if (!inventoryItems || inventoryItems.length === 0) {
            const li = document.createElement('li');
            li.textContent = 'No equipment';
            equipmentList.appendChild(li);
            return;
        }
        
        // Add each item to the equipment list
        inventoryItems.forEach(item => {
            const li = document.createElement('li');
            if (typeof item === 'string') {
                li.textContent = item;
            } else {
                li.textContent = item.name || 'Unknown item';
            }
            equipmentList.appendChild(li);
        });
    }

    function addJournalEntry(entry) {
        if (!journalContent) return;
        
        if (journalContent.textContent.trim() === 'No journal entries yet.') {
            journalContent.innerHTML = '';
        }
        
        const entryDiv = document.createElement('div');
        entryDiv.classList.add('journal-entry');
        
        const dateDiv = document.createElement('div');
        dateDiv.classList.add('entry-date');
        dateDiv.textContent = entry.date;
        
        const textDiv = document.createElement('div');
        textDiv.classList.add('entry-text');
        textDiv.textContent = entry.text;
        
        entryDiv.appendChild(dateDiv);
        entryDiv.appendChild(textDiv);
        journalContent.appendChild(entryDiv);
        
        // Scroll to bottom
        journalContent.scrollTop = journalContent.scrollHeight;
    }

    // Handle command input
    commandInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const command = commandInput.value.trim();
            if (command) {
                // Add to history
                gameHistory.push(command);
                historyIndex = gameHistory.length;

                // Send command to server
                sendCommand(command);

                // Clear input
                commandInput.value = '';
            }
            e.preventDefault();
        } else if (e.key === 'ArrowUp') {
            // Navigate history
            if (historyIndex > 0) {
                historyIndex--;
                commandInput.value = gameHistory[historyIndex];
            }
            e.preventDefault();
        } else if (e.key === 'ArrowDown') {
            // Navigate history
            if (historyIndex < gameHistory.length - 1) {
                historyIndex++;
                commandInput.value = gameHistory[historyIndex];
            } else if (historyIndex === gameHistory.length - 1) {
                historyIndex = gameHistory.length;
                commandInput.value = '';
            }
            e.preventDefault();
        }
    });

    // Load character data from API
    async function loadCharacterData(id) {
        if (!id) {
            console.error("Invalid character ID:", id);
            return false;
        }
        
        try {
            console.log(`Attempting to load character data for ID: ${id}`);
            
            // First, ensure we have the character in our list of characters
            if (!characters || characters.length === 0) {
                try {
                    // If we don't have characters yet, try to load them
                    console.log("No characters loaded yet, fetching list from server");
                    characters = await loadCharacters();
                    console.log("Loaded characters:", characters);
                } catch (error) {
                    console.error("Error loading characters list:", error);
                    // Continue anyway, we'll handle this below
                }
            }

            // Try to find the character in our current list
            const cachedCharacter = characters.find(c => String(c.id) === String(id));
            if (cachedCharacter) {
                console.log(`Found cached character: ${cachedCharacter.name}`);
            } else {
                console.log(`No cached character found for ID: ${id}`);
                // Clear the invalid character ID if it's not in our list
                if (characters && characters.length > 0) {
                    console.warn("Character ID not found in available characters, clearing it");
                    return false;
                }
            }
            
            // Make API request to get full character details
            console.log(`Making API request for character ${id}`);
            const response = await fetch(`/api/characters/${id}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                console.warn(`API error: ${response.status} - ${response.statusText}`);
                
                // If we failed but have cached data, use that
                if (cachedCharacter) {
                    console.warn("Using cached character data due to API error");
                    updateCharacterInfo(cachedCharacter);
                    return true; // Return success, we can use the cached data
                }
                
                // If API failed and no cached data, clear the character ID
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const character = await response.json();
            console.log(`API returned character:`, character);
            
            // Merge with cached data if needed (API might return partial data)
            const mergedCharacter = { 
                ...cachedCharacter,  // Include cached data as baseline
                ...character         // Override with fresh data from API
            };
            
            // Update UI with character info
            updateCharacterInfo(mergedCharacter);

            // Also try to load inventory and journal, but don't fail if they error
            try {
                await loadInventory(id);
            } catch (error) {
                console.warn("Error loading inventory, continuing:", error);
            }

            try {
                await loadJournal(id);
            } catch (error) {
                console.warn("Error loading journal, continuing:", error);
            }

            return true;
        } catch (error) {
            console.error("Error loading character data:", error);
            
            // Look for cached character data as a fallback
            if (characters && characters.length > 0) {
                const cachedCharacter = characters.find(c => String(c.id) === String(id));
                if (cachedCharacter) {
                    console.warn("Using cached character data due to API error");
                    updateCharacterInfo(cachedCharacter);
                    return true; // Still consider this success since we have some data
                }
            }
            
            return false;
        }
    }

    // Load inventory for a character
    async function loadInventory(characterId) {
        try {
            const response = await fetch(`/api/characters/${characterId}/inventory`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const inventoryData = await response.json();
            updateInventory(inventoryData.items);
            return true;
        } catch (error) {
            console.error("Error loading inventory:", error);
            return false;
        }
    }

    // Load journal for a character
    async function loadJournal(characterId) {
        try {
            const response = await fetch(`/api/characters/${characterId}/journal`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const journalData = await response.json();
            
            // Clear existing entries
            journalContent.innerHTML = '';
            
            // Add each entry
            if (journalData.entries && journalData.entries.length > 0) {
                journalData.entries.forEach(entry => {
                    addJournalEntry(entry);
                });
            } else {
                journalContent.textContent = 'No journal entries yet.';
            }
            
            return true;
        } catch (error) {
            console.error("Error loading journal:", error);
            return false;
        }
    }

    // Select a character by name
    function selectCharacterByName(name) {
        if (!characters || characters.length === 0) {
            // Load characters first then try to select
            loadCharacters()
                .then(chars => {
                    characters = chars;
                    trySelectCharacter();
                })
                .catch(error => {
                    console.error("Error loading characters:", error);
                    displayMessage("Error loading characters. Please try again later.", "error");
                });
        } else {
            trySelectCharacter();
        }

        function trySelectCharacter() {
            // Find the character that matches the name (case insensitive)
            const character = characters.find(c => 
                c.name.toLowerCase() === name.toLowerCase() ||
                c.name.toLowerCase().includes(name.toLowerCase())
            );

            if (character) {
                selectCharacter(character.id);
                displayMessage(`Selected character: ${character.name}`, "system");
            } else {
                displayMessage(`Character "${name}" not found. Type "characters" to see available characters.`, "error");
            }
        }
    }

    // Start the game
    initGame();
});
