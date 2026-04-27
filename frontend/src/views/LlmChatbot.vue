<template>
    <div class="chatbot-container">
        <div class="chat-messages">
            <div v-for="(msg, idx) in messages" :key="idx" :class="msg.role">
                <span>{{ msg.role === 'user' ? 'You' : 'Bot' }}:</span> {{ msg.content }}
            </div>
        </div>
        <form @submit.prevent="sendMessage" class="chat-input">
            <input v-model="input" type="text" placeholder="Type your message..." required />
            <button type="submit">Send</button>
        </form>
    </div>
</template>

<script>
export default {
    name: 'LlmChatbot',
    data() {
        return {
            input: '',
            messages: []
        };
    },
    methods: {
        async sendMessage() {
            if (!this.input.trim()) return;
            const userMsg = { role: 'user', content: this.input };
            this.messages.push(userMsg);
            const userInput = this.input;
            this.input = '';
            try {
                const res = await fetch(import.meta.env.VITE_API_URL + '/llm_chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: userInput })
                });
                const data = await res.json();
                if (data.reply) {
                    this.messages.push({ role: 'bot', content: data.reply });
                } else {
                    this.messages.push({ role: 'bot', content: 'Sorry, no response.' });
                }
            } catch (err) {
                this.messages.push({ role: 'bot', content: 'You will get response shortly' });
            }
        }
    }
};
</script>

<style scoped>
.chatbot-container {
    border: 1px solid #ccc;
    border-radius: 8px;
    max-width: 400px;
    margin: 0 auto;
    padding: 16px;
    background: #fafafa;
}

.chat-messages {
    min-height: 200px;
    max-height: 300px;
    overflow-y: auto;
    margin-bottom: 12px;
}

.user {
    text-align: right;
    color: #1976d2;
    margin-bottom: 4px;
}

.bot {
    text-align: left;
    color: #388e3c;
    margin-bottom: 4px;
}

.chat-input {
    display: flex;
    gap: 8px;
}

.chat-input input {
    flex: 1;
    padding: 6px 8px;
    border-radius: 4px;
    border: 1px solid #ccc;
}

.chat-input button {
    padding: 6px 16px;
    border-radius: 4px;
    border: none;
    background: #1976d2;
    color: #fff;
    cursor: pointer;
}
</style>
