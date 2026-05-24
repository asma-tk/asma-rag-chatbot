// Configuration
const API_URL = 'https://asma-rag-chatbot-2.onrender.com';
let conversationHistory = [];

// Éléments DOM
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const typingIndicator = document.getElementById('typingIndicator');
const suggestions = document.querySelectorAll('.suggestion-chip');

// Fonction pour ajouter un message au chat
function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    // Avatar seulement pour le bot
    if (!isUser) {
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = '<img src="robot.png" alt="Robot" class="robot-avatar">';
        messageDiv.appendChild(avatarDiv);
    }
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    
    // Convertir les retours à la ligne en <br>
    const formattedContent = content.replace(/\n/g, '<br>');
    textDiv.innerHTML = formattedContent;
    
    contentDiv.appendChild(textDiv);
    messageDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll vers le bas avec animation fluide
    setTimeout(() => {
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
}

// Fonction pour afficher/masquer l'indicateur de frappe
function showTypingIndicator(show = true) {
    typingIndicator.style.display = show ? 'block' : 'none';
    if (show) {
        setTimeout(() => {
            chatMessages.scrollTo({
                top: chatMessages.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
    }
}

// Fonction pour envoyer un message à l'API
async function sendMessage(message) {
    try {
        // Ajouter le message de l'utilisateur à l'historique
        conversationHistory.push({
            role: 'user',
            content: message
        });
        
        // Afficher l'indicateur de frappe
        showTypingIndicator(true);
        
        // Envoyer la requête à l'API
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                conversation_history: conversationHistory
            })
        });
        
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Masquer l'indicateur de frappe
        showTypingIndicator(false);
        
        // Ajouter la réponse du bot
        addMessage(data.response, false);
        
        // Ajouter la réponse à l'historique
        conversationHistory.push({
            role: 'assistant',
            content: data.response
        });
        
        // Limiter l'historique à 10 messages
        if (conversationHistory.length > 10) {
            conversationHistory = conversationHistory.slice(-10);
        }
        
    } catch (error) {
        console.error('Erreur lors de l\'envoi du message:', error);
        showTypingIndicator(false);
        
        // Message d'erreur élégant
        addMessage(
            "Désolé, je rencontre un problème technique. 😔\n\n" +
            "Assurez-vous que le serveur est démarré avec la commande:\n" +
            "python app.py\n\n" +
            "Erreur: " + error.message,
            false
        );
    }
}

// Fonction pour gérer l'envoi du message
function handleSendMessage() {
    const message = userInput.value.trim();
    
    if (message === '') return;
    
    // Ajouter le message de l'utilisateur
    addMessage(message, true);
    
    // Vider l'input
    userInput.value = '';
    
    // Envoyer le message à l'API
    sendMessage(message);
}

// Event listeners
sendButton.addEventListener('click', handleSendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
    }
});

// Gérer les suggestions
suggestions.forEach(suggestion => {
    suggestion.addEventListener('click', () => {
        const message = suggestion.textContent;
        userInput.value = message;
        handleSendMessage();
    });
});

// Auto-focus sur l'input au chargement
window.addEventListener('load', () => {
    userInput.focus();
    checkServerStatus();
});

// Vérifier le statut du serveur
async function checkServerStatus() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Serveur connecté:', data);
            
            // Afficher un message de bienvenue personnalisé
            if (data.chroma_documents > 0) {
                console.log(`📚 Base de connaissances chargée: ${data.chroma_documents} documents`);
            }
        }
    } catch (error) {
        console.warn('⚠️ Serveur non disponible. Démarrez-le avec: python app.py');
        
        // Afficher un message d'avertissement dans le chat
        setTimeout(() => {
            addMessage(
                "⚠️ Le serveur n'est pas démarré.\n\n" +
                "Pour utiliser le chatbot, veuillez:\n" +
                "1. Ouvrir un terminal\n" +
                "2. Activer l'environnement virtuel: source venv/bin/activate\n" +
                "3. Lancer le serveur: python app.py\n\n" +
                "Le chatbot sera alors opérationnel ! 🚀",
                false
            );
        }, 1000);
    }
}

// Vérifier périodiquement la connexion
setInterval(checkServerStatus, 30000); // Toutes les 30 secondes

// Animation au survol des messages
chatMessages.addEventListener('mouseover', (e) => {
    const message = e.target.closest('.message');
    if (message) {
        message.style.transform = 'scale(1.01)';
        message.style.transition = 'transform 0.2s ease';
    }
});

chatMessages.addEventListener('mouseout', (e) => {
    const message = e.target.closest('.message');
    if (message) {
        message.style.transform = 'scale(1)';
    }
});

// Empêcher le zoom sur mobile lors du focus de l'input
if (/iPhone|iPad|iPod|Android/i.test(navigator.userAgent)) {
    const viewport = document.querySelector('meta[name=viewport]');
    viewport.setAttribute('content', 
        'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
    );
}

// Gestion du redimensionnement de la fenêtre
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 250);
});

// Easter egg: commandes spéciales
userInput.addEventListener('input', (e) => {
    const value = e.target.value.toLowerCase();
    
    // Commande pour effacer l'historique
    if (value === '/clear') {
        conversationHistory = [];
        chatMessages.innerHTML = '';
        
        // Réafficher le message de bienvenue
        addMessage(
            "Historique effacé ! 🧹\n\n" +
            "Vous pouvez recommencer une nouvelle conversation.",
            false
        );
        
        userInput.value = '';
    }
    
    // Commande pour afficher les stats
    if (value === '/stats') {
        fetch(`${API_URL}/stats`)
            .then(res => res.json())
            .then(data => {
                addMessage(
                    `📊 Statistiques du système:\n\n` +
                    `• Documents indexés: ${data.total_documents}\n` +
                    `• Modèle IA: ${data.model}\n` +
                    `• Modèle d'embeddings: ${data.embedding_model}\n` +
                    `• Messages dans l'historique: ${conversationHistory.length}`,
                    false
                );
            })
            .catch(err => {
                addMessage("Impossible de récupérer les statistiques.", false);
            });
        
        userInput.value = '';
    }
});

// Log de démarrage
console.log(`
╔═══════════════════════════════════════════╗
║   🤖 Chatbot Personnel - Asma Taberkokt   ║
║                                           ║
║   Système RAG avec:                       ║
║   • FastAPI                               ║
║   • ChromaDB                              ║
║   • LangChain                             ║
║   • Claude AI                             ║
║                                           ║
║   Commandes spéciales:                    ║
║   • /clear - Effacer l'historique        ║
║   • /stats - Afficher les statistiques   ║
╚═══════════════════════════════════════════╝
`);

// Made with Bob
