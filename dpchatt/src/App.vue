<template>
  <div class="chat-container">
    <div class="main-panel">
      <!-- 左侧边栏：对话历史和TTS控制 -->
      <div class="sidebar" v-if="showSidebar">
        <div class="conversation-sidebar">
          <!-- 工具栏区域 -->
          <div class="sidebar-toolbar">
            <button @click="toggleAlwaysOnTop" :class="['toolbar-btn', { 'active': isAlwaysOnTop }]" title="置顶窗口">
              <svg v-if="!isAlwaysOnTop" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 19V5M5 12l7-7 7 7"/>
              </svg>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 5v14M5 12l7 7 7-7"/>
              </svg>
            </button>
            <button @click="toggleDarkMode" :class="['toolbar-btn', { 'active': isDarkMode }]" title="深色模式">
              <svg v-if="!isDarkMode" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="5"/>
                <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
              </svg>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
              </svg>
            </button>
          </div>
          <div class="sidebar-header">
            <h2>对话历史</h2>
            <button @click="createNewConversation" class="new-chat-btn">
              <span class="icon">+</span> 新对话
            </button>
          </div>
          <div class="conversation-list">
            <div
              v-for="conv in conversations"
              :key="conv.id"
              :class="['conversation-item', { active: currentConversationId === conv.id }]"
              @click="switchConversation(conv.id)"
            >
              <div class="conversation-title">{{ conv.title || '新对话' }}</div>
              <div class="conversation-time">{{ formatTime(conv.createdAt) }}</div>
              <button @click.stop="deleteConversation(conv.id)" class="delete-btn">×</button>
            </div>
          </div>
        </div>
        <div class="tts-controls">
          <h2>文本转语音(TTS)</h2>
          <div class="tts-status">
            <span>开启语音回答: </span>
            <label class="switch">
              <input type="checkbox" v-model="autoSpeak">
              <span class="slider round"></span>
            </label>
          </div>
          <div class="manual-input">
            <h3>手动输入朗读</h3>
            <textarea
              v-model="textToSpeak"
              placeholder="请输入要转换的文字"
              rows="4"
            ></textarea>
            <div class="tts-buttons">
              <button @click="speakText" :disabled="isSpeaking">
                {{ isSpeaking ? '正在播放...' : '播放语音' }}
              </button>
              <button @click="stopSpeaking" :disabled="!isSpeaking">
                停止播放
              </button>
            </div>
          </div>
          <audio ref="audioPlayer" controls style="display:none"></audio>
        </div>
      </div>

      <!-- 右侧：聊天框 -->
      <div class="chat-box">
        <div class="chat-toolbar">
          <button @click="toggleSidebar" :class="['toolbar-btn', { 'active': !showSidebar }]" title="切换侧边栏">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 12h18M3 6h18M3 18h18"/>
            </svg>
          </button>
          <button @click="showDebugPanel = !showDebugPanel" :class="['toolbar-btn', { 'active': showDebugPanel }]" title="调试面板">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
            </svg>
          </button>
        </div>
        <div class="chat-messages" ref="chatMessages">
          <div v-for="(message, index) in chatHistory" :key="index" :class="['message', message.role]">
            <div class="message-avatar">
              <img v-if="message.role === 'user'" :src="userAvatar" alt="User">
              <img v-else :src="agentAvatar" alt="Bot">
            </div>
            <div class="message-content">{{ message.content }}</div>
          </div>
          <div v-if="isTyping" class="message bot typing">
            <div class="message-avatar">
              <img :src="agentAvatar" alt="Bot">
            </div>
            <div class="message-content">
              <span class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </span>
            </div>
          </div>
        </div>
        <div class="chat-input-area">
          <div class="input-wrapper">
            <textarea
              v-model="userInput"
              placeholder="请输入消息..."
              rows="2"
              @keydown.enter.prevent="sendMessage"
              :disabled="isTyping"
            ></textarea>
            <button
              @click="toggleRecording"
              :class="['record-btn', { 'recording': isRecording }]"
              :disabled="isTyping"
            >
              {{ isRecording ? '停止录音' : '开始录音' }}
            </button>
          </div>
          <button @click="sendMessage" :disabled="!userInput.trim() || isTyping">
            发送
          </button>
        </div>
      </div>
    </div>

    <!-- 调试面板按钮已移至顶部工具栏 -->

    <!-- 调试面板组件 -->
    <DebugPanel ref="debugPanel" :show="showDebugPanel" @toggle="showDebugPanel = !showDebugPanel" />
  </div>
</template>

<script>
import DebugPanel from './components/debugpanel.vue'

export default {
  name: 'App',
  components: {
    DebugPanel
  },
  data() {
    return {
      textToSpeak: '',
      isSpeaking: false,
      autoSpeak: false,
      isRecording: false,
      audioContext: null,
      mediaStream: null,
      processor: null,
      audioBuffer: [],
      lastBotMessage: '',
      difyApiKey: '输入dify对应agent的api',
      difyApiUrl: 'https://api.dify.ai/v1',
      conversationId: null,
      userId: 'user-' + Math.random().toString(36).substring(7),
      userInput: '',
      chatHistory: [],
      isTyping: false,
      agentAvatar: 'https://images.unsplash.com/photo-1773847840210-768347cc0d23?w=700&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwcm9maWxlLXBhZ2V8MXx8fGVufDB8fHx8fA%3D%3D',
      userAvatar: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=700&auto=format&fit=crop&q=60',
      isAlwaysOnTop: false,
      isDarkMode: true,
      showDebugPanel: false,
      agentAvatars: [
        'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1475924156734-496f6cac6ec1?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1472214103451-9374bd1c798e?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1433086966358-54859d0ed716?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1475924156734-496f6cac6ec1?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1472214103451-9374bd1c798e?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1433086966358-54859d0ed716?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1475924156734-496f6cac6ec1?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1472214103451-9374bd1c798e?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1433086966358-54859d0ed716?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=700&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1475924156734-496f6cac6ec1?w=700&auto=format&fit=crop&q=60'
      ],
      conversations: [],
      currentConversationId: null,
      showSidebar: true
    }
  },
  mounted() {
    // 组件挂载时加载对话历史
    this.loadConversations();

    // 加载深色模式设置
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode !== null) {
      this.isDarkMode = JSON.parse(savedDarkMode);
      if (this.isDarkMode) {
        document.body.classList.add('dark-mode');
      }
    }

    // 如果没有对话历史，创建一个新对话
    if (this.conversations.length === 0) {
      this.createNewConversation();
    } else {
      // 加载最近的对话
      this.switchConversation(this.conversations[0].id);
      // 确保显示正确的头像
      this.$nextTick(() => {
        this.updateCurrentAgentAvatar();
      });
    }
  },
  beforeUnmount() {
    // 组件卸载前的清理操作
  },
  methods: {
    // 加载对话历史
    loadConversations() {
      try {
        const savedConversations = localStorage.getItem('chat_conversations');
        if (savedConversations) {
          this.conversations = JSON.parse(savedConversations);
        }
      } catch (error) {
        console.error('加载对话历史失败:', error);
        this.conversations = [];
      }
    },
    // 保存对话历史
    saveConversations() {
      try {
        localStorage.setItem('chat_conversations', JSON.stringify(this.conversations));
      } catch (error) {
        console.error('保存对话历史失败:', error);
      }
    },
    // 创建新对话
    createNewConversation() {
      const newConversation = {
        id: Date.now().toString(),
        title: '新对话',
        createdAt: new Date().toISOString(),
        messages: [],
        difyConversationId: null,
        agentAvatar: this.agentAvatar
      };
      this.conversations.unshift(newConversation);
      this.currentConversationId = newConversation.id;
      this.chatHistory = [];
      this.conversationId = null;
      // 更新当前对话的头像
      this.updateCurrentAgentAvatar();
      this.saveConversations();
      this.$nextTick(() => {
        this.scrollToBottom();
      });
    },
    // 切换对话
    switchConversation(conversationId) {
      const conversation = this.conversations.find(c => c.id === conversationId);
      if (conversation) {
        this.currentConversationId = conversationId;
        this.chatHistory = [...conversation.messages];
        this.conversationId = conversation.difyConversationId || null;
        // 更新当前对话的头像
        this.updateCurrentAgentAvatar();
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      }
    },
    // 删除对话
    deleteConversation(conversationId) {
      this.conversations = this.conversations.filter(c => c.id !== conversationId);
      this.saveConversations();

      // 如果删除的是当前对话，切换到其他对话或创建新对话
      if (this.currentConversationId === conversationId) {
        if (this.conversations.length > 0) {
          this.switchConversation(this.conversations[0].id);
        } else {
          this.createNewConversation();
        }
      }
    },
    // 更新当前对话
    updateCurrentConversation() {
      const conversation = this.conversations.find(c => c.id === this.currentConversationId);
      if (conversation) {
        conversation.messages = [...this.chatHistory];
        conversation.difyConversationId = this.conversationId;

        // 如果对话标题为"新对话"且有用户消息，使用第一条用户消息作为标题
        if (conversation.title === '新对话' && this.chatHistory.length > 0) {
          const firstUserMessage = this.chatHistory.find(m => m.role === 'user');
          if (firstUserMessage) {
            conversation.title = firstUserMessage.content.substring(0, 30) + (firstUserMessage.content.length > 30 ? '...' : '');
          }
        }

        this.saveConversations();
      }
    },
    // 更新当前对话的AI头像
    updateCurrentAgentAvatar() {
      const conversation = this.conversations.find(c => c.id === this.currentConversationId);
      if (conversation && conversation.agentAvatar) {
        this.agentAvatar = conversation.agentAvatar;
      }
    },
    // 格式化时间
    formatTime(timestamp) {
      const date = new Date(timestamp);
      const now = new Date();


      // 如果是今天
      if (date.toDateString() === now.toDateString()) {
        return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
      }
      // 如果是昨天
      const yesterday = new Date(now);
      yesterday.setDate(yesterday.getDate() - 1);
      if (date.toDateString() === yesterday.toDateString()) {
        return '昨天';
      }
      // 其他日期
      return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
    },
    // 切换置顶窗口
    toggleAlwaysOnTop() {
      this.isAlwaysOnTop = !this.isAlwaysOnTop;
      // 通过IPC通信通知主进程切换置顶状态
      if (window.require) {
        const { ipcRenderer } = window.require('electron');
        ipcRenderer.send('toggle-always-on-top', this.isAlwaysOnTop);
      }
    },
    // 切换深色模式
    toggleDarkMode() {
      this.isDarkMode = !this.isDarkMode;
      // 保存深色模式设置
      localStorage.setItem('darkMode', this.isDarkMode);
      // 切换深色模式样式
      if (this.isDarkMode) {
        document.body.classList.add('dark-mode');
      } else {
        document.body.classList.remove('dark-mode');
      }
    },
    // 切换侧边栏
    toggleSidebar() {
      this.showSidebar = !this.showSidebar;
    },

    async sendMessage() {
      if (!this.userInput.trim() || this.isTyping) return;

      const message = this.userInput.trim();
      this.userInput = '';

      // 添加用户消息到聊天历史
      this.chatHistory.push({
        role: 'user',
        content: message
      });

      // 滚动到底部
      this.$nextTick(() => {
        this.scrollToBottom();
      });

      // 设置为正在输入状态
      this.isTyping = true;

      try {
        // 调用Dify API获取回复,使用流式响应
        await this.sendToDify(message);

        // 移除正在输入状态
        this.isTyping = false;
      } catch (error) {
        this.isTyping = false;
        console.error('发送消息失败:', error);
        alert('发送消息失败，请重试');
      }
    },
    scrollToBottom() {
      const chatMessages = this.$refs.chatMessages;
      if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
      }
    },
    // 开始录音
    async toggleRecording() {
      if (this.isRecording) {
        // 停止录音
        await this.stopRecording();
      } else {
        // 开始录音
        await this.startRecording();
      }
    },
    // 开始录音
    async startRecording() {
      try {
        // 请求麦克风权限
        this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });

        // 创建音频上下文
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });

        // 创建音频源
        const source = this.audioContext.createMediaStreamSource(this.mediaStream);

        // 创建脚本处理器
        const bufferSize = 4096;
        this.processor = this.audioContext.createScriptProcessor(bufferSize, 1, 1);

        // 连接音频节点
        source.connect(this.processor);
        this.processor.connect(this.audioContext.destination);

        // 处理音频数据
        this.processor.onaudioprocess = (event) => {
          const audioData = event.inputBuffer.getChannelData(0);
          this.audioBuffer.push(...audioData);

          // 识别将在停止录音时触发
        };

        // 不设置自动停止，录音将持续直到用户手动停止

        this.isRecording = true;
        console.log('开始录音...');

      } catch (error) {
        console.error('录音失败:', error);
        alert('无法访问麦克风，请检查权限设置');
      }
    },
    // 处理音频数据
    async processAudio() {
      if (!this.isRecording || this.audioBuffer.length < 16000) {
        return;
      }
    },
    // 创建WAV格式的音频数据
    createWav(int16Data) {
      const buffer = new ArrayBuffer(44 + int16Data.length * 2);
      const view = new DataView(buffer);

      // WAV文件头
      const writeString = (view, offset, string) => {
        for (let i = 0; i < string.length; i++) {
          view.setUint8(offset + i, string.charCodeAt(i));
        }
      };

      writeString(view, 0, 'RIFF');
      view.setUint32(4, 36 + int16Data.length * 2, true);
      writeString(view, 8, 'WAVE');
      writeString(view, 12, 'fmt ');
      view.setUint32(16, 16, true);
      view.setUint16(20, 1, true);
      view.setUint16(22, 1, true);
      view.setUint32(24, 16000, true);
      view.setUint32(28, 32000, true);
      view.setUint16(32, 2, true);
      view.setUint16(34, 16, true);
      writeString(view, 36, 'data');
      view.setUint32(40, int16Data.length * 2, true);

      // 写入音频数据
      for (let i = 0; i < int16Data.length; i++) {
        view.setInt16(44 + i * 2, int16Data[i], true);
      }

      return buffer;
    },
    // 停止录音
    async stopRecording() {
      if (this.processor) {
        this.processor.disconnect();
        this.processor = null;
      }

      if (this.audioContext) {
        this.audioContext.close();
        this.audioContext = null;
      }

      if (this.mediaStream) {
        this.mediaStream.getTracks().forEach(track => track.stop());
        this.mediaStream = null;
      }

      this.isRecording = false;
      console.log('停止录音');

      // 如果有音频数据，进行处理和识别
      if (this.audioBuffer.length > 0) {
        await this.processAllAudio();
      }

      this.audioBuffer = [];
    },
    // 处理所有音频数据
    async processAllAudio() {
      if (this.audioBuffer.length === 0) {
        return;
      }

      try {
        // 转换为Int16格式
        const int16Data = new Int16Array(this.audioBuffer.length);
        for (let i = 0; i < this.audioBuffer.length; i++) {
          int16Data[i] = Math.max(-32768, Math.min(32767, this.audioBuffer[i] * 32768));
        }

        // 创建WAV格式的音频数据
        const wavData = this.createWav(int16Data);

        // 创建Blob
        const audioBlob = new Blob([wavData], { type: 'audio/wav' });

        // 发送到STT服务器进行识别
        await this.transcribeAudio(audioBlob);

      } catch (error) {
        console.error('处理音频数据失败:', error);
      }
    },
    // 语音识别
    async transcribeAudio(audioBlob) {
      try {
        const logMessage = '开始语音识别...';
        console.log(logMessage);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: logMessage
        });

        // 创建FormData对象
        const formData = new FormData();
        formData.append('file', audioBlob, 'audio.wav');

        // 发送到STT服务器
        const response = await fetch('http://localhost:8006/transcribe', {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          const errorText = await response.text();
          const errorMessage = `HTTP错误: ${response.status} - ${errorText}`;
          console.error('HTTP错误:', response.status, errorText);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'error',
            message: errorMessage
          });
          throw new Error(errorMessage);
        }

        const result = await response.json();
        console.log('服务器响应:', result);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: `服务器响应: ${JSON.stringify(result)}`
        });

        if (result.success) {
          // 检查是否有识别结果
          if (result.text && result.text.trim()) {
            // 将识别的文本添加到输入框
            this.userInput = result.text;
            const successMessage = `识别结果: ${result.text}`;
            console.log(successMessage);
            this.$refs.debugPanel?.addLog({
              timestamp: new Date().toISOString(),
              type: 'success',
              message: successMessage
            });
          } else {
            const emptyMessage = '本次识别结果为空，可能是静音片段';
            console.log(emptyMessage);
            this.$refs.debugPanel?.addLog({
              timestamp: new Date().toISOString(),
              type: 'warning',
              message: emptyMessage
            });
          }
        } else {
          const errorMessage = `语音识别失败: ${result.error || '未知错误'}`;
          console.error(errorMessage);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'error',
            message: errorMessage
          });
        }
      } catch (error) {
        const errorMsg = `语音识别错误: ${error.message}`;
        console.error(errorMsg);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'error',
          message: errorMsg
        });
      }
    },
    async speakText(text) {
      // 处理传入的参数，确保是字符串类型
      let textToProcess = text || this.textToSpeak;

      // 如果传入的是事件对象，使用textToSpeak
      if (text && typeof text !== 'string' && text.target) {
        textToProcess = this.textToSpeak;
      }

      // 确保textToProcess是字符串类型
      textToProcess = String(textToProcess || '');

      if (!textToProcess.trim()) {
        if (!text) {
          alert('请输入要转换的文字');
        }
        return;
      }

      this.isSpeaking = true;
      try {
        const logMessage = `开始语音合成: ${textToProcess.substring(0, 50)}${textToProcess.length > 50 ? '...' : ''}`;
        console.log(logMessage);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: logMessage
        });

        const response = await fetch('http://localhost:8000/tts_dify', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ text: textToProcess })
        });

        if (!response.ok) {
          const errorMessage = '语音合成请求失败';
          console.error(errorMessage);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'error',
            message: errorMessage
          });
          throw new Error(errorMessage);
        }

        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = this.$refs.audioPlayer;
        audio.src = audioUrl;
        audio.play();

        const successMessage = '语音合成成功，开始播放';
        console.log(successMessage);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'success',
          message: successMessage
        });

        audio.onended = () => {
          this.isSpeaking = false;
          URL.revokeObjectURL(audioUrl);
          const endMessage = '语音播放完成';
          console.log(endMessage);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'info',
            message: endMessage
          });
        };
      } catch (error) {
        const errorMsg = `TTS错误: ${error.message}`;
        console.error(errorMsg);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'error',
          message: errorMsg
        });
        alert('语音合成失败，请确保TTS服务器正在运行');
        this.isSpeaking = false;
      }
    },
    stopSpeaking() {
      const audio = this.$refs.audioPlayer;
      if (audio) {
        audio.pause();
        audio.currentTime = 0;
        this.isSpeaking = false;
      }
    },
    // 执行截图
    async takeScreenshot() {
      try {
        const logMessage = '正在执行截图...';
        console.log(logMessage);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: logMessage
        });

        const response = await fetch('http://localhost:8001/screenshot', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ message: this.lastBotMessage })
        });

        if (!response.ok) {
          throw new Error('截图请求失败');
        }

        const result = await response.json();
        console.log('截图结果:', result);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: `截图结果: ${JSON.stringify(result)}`
        });

        if (result.success) {
          const successMessage = `截图成功: ${result.screenshot_path}`;
          console.log(successMessage);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'success',
            message: successMessage
          });
          // 可以在这里添加显示截图的逻辑
        } else {
          const errorMessage = `截图失败: ${result.message}`;
          console.error(errorMessage);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'error',
            message: errorMessage
          });
        }
      } catch (error) {
        const errorMsg = `截图错误: ${error.message}`;
        console.error(errorMsg);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'error',
          message: errorMsg
        });
        alert('截图失败，请确保截图服务器正在运行');
      }
    },

    // 移除括号内的内容和标点符号，用于朗读
    cleanResponse(text) {
      // 移除括号内的内容
      let cleaned = text.replace(/\([^)]*\)/g, '');
      // 移除中文括号内的内容
      cleaned = cleaned.replace(/（[^）]*）/g, '');
      // 移除所有标点符号（包括中文和英文标点）
      cleaned = cleaned.replace(/[\p{P}\p{S}]/gu, '');
      // 移除多余的空格
      cleaned = cleaned.replace(/\s+/g, ' ').trim();
      return cleaned;
    },
    // 发送QQ消息
    async sendQQMessage(message) {
      try {
        const logMessage = `正在发送QQ消息: ${message}`;
        console.log(logMessage);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: logMessage
        });

        const response = await fetch('http://localhost:8002/send_qq_message', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message: message
          })
        });

        if (!response.ok) {
          const errorMessage = 'QQ消息请求失败';
          console.error(errorMessage);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'error',
            message: errorMessage
          });
          throw new Error(errorMessage);
        }

        const result = await response.json();
        console.log('QQ消息结果:', result);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: `QQ消息结果: ${JSON.stringify(result)}`
        });

        if (result.success) {
          const successMessage = `QQ消息发送成功: ${result.message}`;
          console.log(successMessage);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'success',
            message: successMessage
          });
        } else {
          const errorMessage = `QQ消息发送失败: ${result.message}`;
          console.error(errorMessage);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'error',
            message: errorMessage
          });
        }
      } catch (error) {
        const errorMsg = `QQ消息错误: ${error.message}`;
        console.error(errorMsg);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'error',
          message: errorMsg
        });
        alert('QQ消息发送失败，请确保QQ消息服务正在运行');
      }
    },

    // 打开单个网站
    async openWebsite(url) {
      try {
        const logMessage = `正在打开网站: ${url}`;
        console.log(logMessage);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: logMessage
        });

        const response = await fetch('http://localhost:8004/open_website_from_message', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message: url
          })
        });

        if (!response.ok) {
          const errorMessage = '打开网站请求失败';
          console.error(errorMessage);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'error',
            message: errorMessage
          });
          throw new Error(errorMessage);
        }

        const result = await response.json();
        console.log('打开网站结果:', result);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: `打开网站结果: ${JSON.stringify(result)}`
        });

        if (result.success) {
          const successMessage = `成功打开 ${result.count} 个网址: ${JSON.stringify(result.urls)}`;
          console.log(successMessage);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'success',
            message: successMessage
          });
        } else {
          const errorMessage = `打开网站失败: ${result.message}`;
          console.error(errorMessage);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'error',
            message: errorMessage
          });
        }
      } catch (error) {
        const errorMsg = `打开网站错误: ${error.message}`;
        console.error(errorMsg);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'error',
          message: errorMsg
        });
        alert('打开网站失败，请确保网站服务正在运行');
      }
    },
    // 打开软件
    async openSoftware() {
      try {
        const logMessage = '正在启动软件...';
        console.log(logMessage);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: logMessage
        });

        const response = await fetch('http://localhost:8007/api/qq/check_and_start', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ message: this.lastBotMessage })
        });

        if (!response.ok) {
          const errorMessage = '启动软件请求失败';
          console.error(errorMessage);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'error',
            message: errorMessage
          });
          throw new Error(errorMessage);
        }

        const result = await response.json();
        console.log('启动软件结果:', result);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: `启动软件结果: ${JSON.stringify(result)}`
        });

        if (result.status === 'success') {
          if (result.results) {
            // 处理多个软件的启动结果
            const successMessage = '软件启动成功';
            console.log(successMessage);
            this.$refs.debugPanel?.addLog({
              timestamp: new Date().toISOString(),
              type: 'success',
              message: successMessage
            });
            result.results.forEach(item => {
              if (item.status === 'success') {
                const itemSuccess = `成功启动: ${item.software_path}`;
                console.log(itemSuccess);
                this.$refs.debugPanel?.addLog({
                  timestamp: new Date().toISOString(),
                  type: 'success',
                  message: itemSuccess
                });
              } else {
                const itemError = `启动失败: ${item.software_path}, 原因: ${item.message}`;
                console.error(itemError);
                this.$refs.debugPanel?.addLog({
                  timestamp: new Date().toISOString(),
                  type: 'error',
                  message: itemError
                });
              }
            });
          } else {
            // 兼容旧版本单个软件的启动结果
            const successMessage = '软件启动成功';
            console.log(successMessage);
            this.$refs.debugPanel?.addLog({
              timestamp: new Date().toISOString(),
              type: 'success',
              message: successMessage
            });
          }
        } else if (result.status === 'no_action') {
          const noActionMessage = '未检测到启动软件的指令';
          console.log(noActionMessage);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'warning',
            message: noActionMessage
          });
        } else {
          const errorMessage = `软件启动失败: ${result.message}`;
          console.error(errorMessage);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'error',
            message: errorMessage
          });
        }
      } catch (error) {
        const errorMsg = `启动软件错误: ${error.message}`;
        console.error(errorMsg);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'error',
          message: errorMsg
        });
        alert('启动软件失败，请确保软件启动服务正在运行');
      }
    },
    // 执行CMD命令
    async executeCommand(command) {
      try {
        const logMessage = `正在执行CMD命令: ${command}`;
        console.log(logMessage);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: logMessage
        });

        const response = await fetch('http://localhost:8008/process_ai_message', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message: `[ACTION:OPENCMD]${command}`
          })
        });

        if (!response.ok) {
          const errorMessage = 'CMD命令请求失败';
          console.error(errorMessage);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'error',
            message: errorMessage
          });
          throw new Error(errorMessage);
        }

        const result = await response.json();
        console.log('CMD命令执行结果:', result);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: `CMD命令执行结果: ${JSON.stringify(result)}`
        });

        if (result.success) {
          const successMessage = 'CMD命令执行成功';
          console.log(successMessage);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'success',
            message: successMessage
          });
          if (result.results && result.results.length > 0) {
            result.results.forEach(item => {
              if (item.success) {
                const cmdSuccess = `命令执行成功: ${item.details.command}`;
                console.log(cmdSuccess);
                this.$refs.debugPanel?.addLog({
                  timestamp: new Date().toISOString(),
                  type: 'success',
                  message: cmdSuccess
                });
                if (item.details.stdout) {
                  const outputMsg = `输出: ${item.details.stdout}`;
                  console.log(outputMsg);
                  this.$refs.debugPanel?.addLog({
                    timestamp: new Date().toISOString(),
                    type: 'info',
                    message: outputMsg
                  });
                }
              } else {
                const cmdError = `命令执行失败: ${item.details.command}, 错误: ${item.details.stderr}`;
                console.error(cmdError);
                this.$refs.debugPanel?.addLog({
                  timestamp: new Date().toISOString(),
                  type: 'error',
                  message: cmdError
                });
              }
            });
          }
        } else {
          const errorMessage = `CMD命令执行失败: ${result.message}`;
          console.error(errorMessage);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'error',
            message: errorMessage
          });
        }
      } catch (error) {
        const errorMsg = `CMD命令错误: ${error.message}`;
        console.error(errorMsg);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'error',
          message: errorMsg
        });
        alert('CMD命令执行失败，请确保命令执行服务正在运行');
      }
    },
    // 获取所有窗口
    async getWindows() {
      try {
        console.log('正在获取窗口列表...');
        const response = await fetch('http://localhost:8005/get_windows', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ message: this.lastBotMessage })
        });

        if (!response.ok) {
          throw new Error('获取窗口列表请求失败');
        }

        const result = await response.json();
        console.log('窗口列表结果:', result);

        if (result.success && result.windows) {
          console.log(`成功获取 ${result.windows.length} 个窗口`);
          // 将窗口列表转换为可读的文本
          let windowsText = `当前打开的窗口列表 (${result.windows.length}个):\n`;
          result.windows.forEach((window, index) => {
            windowsText += `${index + 1}. ${window.title}\n`;
          });

          // 添加窗口列表到聊天记录
          this.chatHistory.push({
            role: 'bot',
            content: windowsText
          });

          // 滚动到底部
          this.$nextTick(() => {
            this.scrollToBottom();
          });

          return windowsText;
        } else {
          console.error(`获取窗口列表失败: ${result.message}`);
          return null;
        }
      } catch (error) {
        console.error('获取窗口列表错误:', error);
        alert('获取窗口列表失败，请确保窗口服务正在运行');
        return null;
      }
    },
    // 置顶窗口
    async topWindow(windowTitle) {
      try {
        const logMessage = `正在置顶窗口: ${windowTitle}`;
        console.log(logMessage);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: logMessage
        });

        const response = await fetch('http://localhost:8008/process_ai_message', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message: `[ACTION:TOPWINDOWS]${windowTitle}`
          })
        });

        if (!response.ok) {
          const errorMessage = '置顶窗口请求失败';
          console.error(errorMessage);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'error',
            message: errorMessage
          });
          throw new Error(errorMessage);
        }

        const result = await response.json();
        console.log('置顶窗口结果:', result);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: `置顶窗口结果: ${JSON.stringify(result)}`
        });

        if (result.success && result.results && result.results.length > 0) {
          const topResult = result.results.find(r => r.action === 'set_window_topmost');
          if (topResult && topResult.success) {
            const successMessage = `成功置顶窗口: ${topResult.details.window.title}`;
            console.log(successMessage);
            this.$refs.debugPanel?.addLog({
              timestamp: new Date().toISOString(),
              type: 'success',
              message: successMessage
            });
          } else {
            const errorMessage = `置顶窗口失败: ${topResult ? topResult.message : '未知错误'}`;
            console.error(errorMessage);
            this.$refs.debugPanel?.addLog({
              timestamp: new Date().toISOString(),
              type: 'error',
              message: errorMessage
            });
          }
        } else {
          const errorMessage = `置顶窗口失败: ${result.message}`;
          console.error(errorMessage);
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'error',
            message: errorMessage
          });
        }
      } catch (error) {
        const errorMsg = `置顶窗口错误: ${error.message}`;
        console.error(errorMsg);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'error',
          message: errorMsg
        });
        alert('置顶窗口失败，请确保服务正在运行');
      }
    },
    async sendToDify(message, retryCount = 0) {
      const maxRetries = 2;
      try {
        console.log('发送消息到Dify API:', message);
        console.log('使用API URL:', `${this.difyApiUrl}/chat-messages`);
        console.log('使用API密钥:', this.difyApiKey);
        console.log('会话ID:', this.conversationId);
        console.log(`重试次数: ${retryCount}/${maxRetries}`);

        const response = await fetch(`${this.difyApiUrl}/chat-messages`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.difyApiKey}`,
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
          },
          body: JSON.stringify({
            inputs: {},
            query: message,
            response_mode: 'streaming',
            conversation_id: this.conversationId || '',
            user: this.userId
          })
        });

        console.log('API响应状态:', response.status);
        console.log('API响应状态文本:', response.statusText);

        if (!response.ok) {
          const errorText = await response.text();
          console.error('API错误响应:', errorText);
          throw new Error(`API请求失败: ${response.status} - ${response.statusText}
${errorText}`);
        }

        // 创建新的机器人消息占位符
        const botMessageIndex = this.chatHistory.length;
        this.chatHistory.push({
          role: 'bot',
          content: ''
        });
        this.$nextTick(() => {
          this.scrollToBottom();
        });

        // 处理流式响应
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let aiResponse = '';
        let conversationId = '';
        let isReading = true;
        let allReceivedData = []; // 存储所有接收到的数据
        let lastUpdateTime = 0;
        const updateInterval = 50; // 每50ms更新一次UI

        while (isReading) {
          const { done, value } = await reader.read();

          if (done) {
            isReading = false;
            console.log('========== AI完整回复 ==========');
            console.log('内容:', aiResponse);
            console.log('会话ID:', conversationId);
            console.log('===============================');
          }

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.slice(6);
              if (dataStr === '[DONE]') {
                continue;
              }

              try {
                const data = JSON.parse(dataStr);
                // 将接收到的数据添加到数组中
                allReceivedData.push(data);

                // 更新会话ID
                if (data.conversation_id) {
                  conversationId = data.conversation_id;
                  this.conversationId = conversationId;
                }

                // 根据事件类型处理不同的响应
                if (data.event === 'message' || data.event === 'agent_message') {
                  // 提取AI回复
                  if (data.answer) {
                    aiResponse += data.answer;
                    // 节流更新UI,避免频繁渲染
                    const now = Date.now();
                    if (now - lastUpdateTime >= updateInterval) {
                      this.chatHistory[botMessageIndex].content = aiResponse;
                      this.$nextTick(() => {
                        this.scrollToBottom();
                      });
                      lastUpdateTime = now;
                    }
                  }
                } else if (data.event === 'workflow_finished' || data.event === 'workflow_run') {
                  // 处理工作流完成事件
                  if (data.outputs) {
                    // 尝试从 outputs 中提取文本内容
                    for (const key in data.outputs) {
                      if (typeof data.outputs[key] === 'string') {
                        aiResponse += data.outputs[key];
                      }
                    }
                  }
                }
              } catch (e) {
                console.error('解析响应数据失败:', e);
              }
            }
          }
        }

        // 确保最后一次更新
        if (aiResponse) {
          this.chatHistory[botMessageIndex].content = aiResponse;
          this.$nextTick(() => {
            this.scrollToBottom();
          });
        }

        if (aiResponse) {
          console.log('AI回复:', aiResponse);
          this.lastBotMessage = aiResponse;

          // 保存原始回复用于显示
          let displayResponse = aiResponse;

          // 创建用于朗读的副本,移除指令
          let speakResponse = aiResponse;

          // 并行执行所有动作
          const actions = [];

          // 检查是否包含截图指令
          if (aiResponse.includes('[ACTION:SCREENSHOT]')) {
            actions.push(this.takeScreenshot());
            // 从朗读内容中移除截图指令
            speakResponse = speakResponse.replace('[ACTION:SCREENSHOT]', '').trim();
          }

          // 检查是否包含发送QQ消息指令
          if (aiResponse.includes('[ACTION:SENDMESSAGE]') && aiResponse.includes('[ACTION:SELECTFRIEND]')) {
            console.log('检测到QQ消息指令');
            // 提取消息内容和好友名称
            const messageMatches = [...aiResponse.matchAll(/\[ACTION:SENDMESSAGE\]([^\n[]*)/g)];
            const friendMatches = [...aiResponse.matchAll(/\[ACTION:SELECTFRIEND\]([^\n[]*)/g)];

            console.log('消息匹配结果:', messageMatches);
            console.log('好友匹配结果:', friendMatches);

            if (messageMatches && friendMatches) {
              // 确保消息和好友数量匹配
              const count = Math.min(messageMatches.length, friendMatches.length);
              if (count > 0) {
                for (let i = 0; i < count; i++) {
                  const message = messageMatches[i][1].trim();
                  const friend = friendMatches[i][1].trim();
                  console.log(`提取的消息 ${i + 1}:`, message);
                  console.log(`提取的好友 ${i + 1}:`, friend);
                  // 构建包含标记的消息
                  const qqMessage = `[ACTION:SELECTFRIEND]${friend}[ACTION:SENDMESSAGE]${message}`;
                  actions.push(this.sendQQMessage(qqMessage));
                }
              }
            } else {
              console.log('未能提取消息或好友信息');
            }
            // 从朗读内容中移除指令
            speakResponse = speakResponse.replace(/\[ACTION:SENDMESSAGE\][\s\S]*?\[ACTION:SELECTFRIEND\][\s\S]*?(?=\[|$)/, '').trim();
          }

          // 检查是否包含发送文件指令
          if (aiResponse.includes('[ACTION:SENDFILE]') && aiResponse.includes('[ACTION:SELECTFRIEND]')) {
            console.log('检测到发送文件指令');
            // 提取文件路径和好友名称
            const fileMatches = [...aiResponse.matchAll(/\[ACTION:SENDFILE\]([^\n[]*)/g)];
            const friendMatches = [...aiResponse.matchAll(/\[ACTION:SELECTFRIEND\]([^\n[]*)/g)];

            console.log('文件匹配结果:', fileMatches);
            console.log('好友匹配结果:', friendMatches);

            if (fileMatches && friendMatches) {
              // 确保文件和好友数量匹配
              const count = Math.min(fileMatches.length, friendMatches.length);
              if (count > 0) {
                for (let i = 0; i < count; i++) {
                  const filePath = fileMatches[i][1].trim();
                  const friend = friendMatches[i][1].trim();
                  console.log(`提取的文件 ${i + 1}:`, filePath);
                  console.log(`提取的好友 ${i + 1}:`, friend);
                  // 构建包含标记的消息
                  const qqMessage = `[ACTION:SELECTFRIEND]${friend}[ACTION:SENDFILE]${filePath}`;
                  actions.push(this.sendQQMessage(qqMessage));
                }
              }
            } else {
              console.log('未能提取文件或好友信息');
            }
            // 从朗读内容中移除指令
            speakResponse = speakResponse.replace(/\[ACTION:SENDFILE\][\s\S]*?\[ACTION:SELECTFRIEND\][\s\S]*?(?=\[|$)/, '').trim();
          }

          // 检查是否包含打开网站指令
          if (aiResponse.includes('[ACTION:OPENWEBSITE]')) {
            // 从回复中提取网址
            const urlMatch = aiResponse.match(/\[ACTION:OPENWEBSITE\](https?:\/\/[^\s]+)/);
            if (urlMatch) {
              actions.push(this.openWebsite(urlMatch[1]));
              // 从朗读内容中移除指令和URL
              speakResponse = speakResponse.replace(/\[ACTION:OPENWEBSITE\]https?:\/\/[^\s]+/, '').trim();
            } else {
              // 如果回复中没有网址，从聊天记录中提取所有网址并打开
              const urlPattern = /https?:\/\/[^\s\]"]+/g;
              const urls = aiResponse.match(urlPattern) || [];
              if (urls.length > 0) {
                // 去重后打开所有网址
                const uniqueUrls = [...new Set(urls)];
                for (const url of uniqueUrls) {
                  actions.push(this.openWebsite(url));
                }
              }
            }
            // 从朗读内容中移除指令
            speakResponse = speakResponse.replace('[ACTION:OPENWEBSITE]', '').trim();
          }

          // 检查是否包含获取窗口列表指令
          if (aiResponse.includes('[ACTION:NOWWINDOWS]')) {
            actions.push(this.getWindows());
            // 从朗读内容中移除指令
            speakResponse = speakResponse.replace('[ACTION:NOWWINDOWS]', '').trim();
          }

          // 检查是否包含置顶窗口指令
          if (aiResponse.includes('[ACTION:TOPWINDOWS]')) {
            const windowMatch = aiResponse.match(/\[ACTION:TOPWINDOWS\]([^\n[]*)/);
            if (windowMatch && windowMatch[1]) {
              const windowTitle = windowMatch[1].trim();
              actions.push(this.topWindow(windowTitle));
              // 从朗读内容中移除指令
              speakResponse = speakResponse.replace(/\[ACTION:TOPWINDOWS\][^\n[]*/, '').trim();
            }
          }

          // 检查是否包含打开软件指令
          if (aiResponse.includes('[ACTION:OPENSOFTWARE]')) {
            actions.push(this.openSoftware());
            // 从朗读内容中移除指令
            speakResponse = speakResponse.replace('[ACTION:OPENSOFTWARE]', '').trim();
          }

          // 检查是否包含执行CMD命令指令
          if (aiResponse.includes('[ACTION:OPENCMD]')) {
            console.log('检测到CMD命令指令');
            // 提取命令内容
            const cmdMatches = [...aiResponse.matchAll(/\[ACTION:OPENCMD\]([^\n[]*)/g)];
            console.log('CMD命令匹配结果:', cmdMatches);

            if (cmdMatches && cmdMatches.length > 0) {
              for (const match of cmdMatches) {
                const cmd = match[1].trim();
                console.log('提取的CMD命令:', cmd);
                if (cmd) {
                  actions.push(this.executeCommand(cmd));
                }
              }
            }
            // 从朗读内容中移除指令
            speakResponse = speakResponse.replace(/\[ACTION:OPENCMD\][^\n[]*/g, '').trim();
          }

          // 检查是否包含读取调试日志指令
          if (aiResponse.includes('[ACTION:READLOG]')) {
            console.log('检测到读取调试日志指令');
            // 获取调试面板的所有日志内容
            const debugPanel = this.$refs.debugPanel;
            if (debugPanel && debugPanel.logs && debugPanel.logs.length > 0) {
              // 将所有日志格式化为字符串
              const logsContent = debugPanel.logs.map(log => {
                const time = this.formatTime(log.timestamp);
                return `${time} ${log.message}`;
              }).join('\n');
              
              // 使用setTimeout确保在Vue更新DOM后再设置焦点
              setTimeout(() => {
                // 将日志内容设置到输入框
                this.userInput = logsContent;
                
                // 等待UI更新
                this.$nextTick(() => {
                  // 聚焦到输入框并设置光标位置
                  const textarea = document.querySelector('.chat-input-area textarea');
                  if (textarea) {
                    textarea.focus();
                    // 将光标移动到文本末尾
                    textarea.setSelectionRange(textarea.value.length, textarea.value.length);
                    // 触发input事件以确保Vue正确处理
                    textarea.dispatchEvent(new Event('input', { bubbles: true }));
                    
                    // 模拟按下Enter键
                    const enterEvent = new KeyboardEvent('keydown', {
                      key: 'Enter',
                      code: 'Enter',
                      keyCode: 13,
                      which: 13,
                      bubbles: true,
                      cancelable: true
                    });
                    textarea.dispatchEvent(enterEvent);
                  }
                });
              }, 100);
            }
            // 从朗读内容中移除指令
            speakResponse = speakResponse.replace('[ACTION:READLOG]', '').trim();
          }

          // 如果开启了自动朗读，则朗读AI回复
          if (this.autoSpeak) {
            // 清理用于朗读的内容，移除括号内的内容和标点符号
            const cleanedResponse = this.cleanResponse(speakResponse);
            console.log('清理后的AI回复（用于朗读）:', cleanedResponse);
            actions.push(this.speakText(cleanedResponse));
          }

          // 并发执行所有动作
          await Promise.all(actions);

          // 更新当前对话
          this.updateCurrentConversation();

          // 返回原始回复用于显示,包含所有指令
          return displayResponse;
        } else {
          console.warn('未能从API响应中提取到AI回复');
          console.warn('当前会话ID:', this.conversationId);
          console.warn('当前用户ID:', this.userId);
          console.warn('收到的所有事件数据:', JSON.stringify({
            conversationId: conversationId,
            hasAnswer: !!aiResponse,
            responseLength: aiResponse.length
          }, null, 2));
          console.warn('所有接收到的数据:', JSON.stringify(allReceivedData, null, 2));

          // 如果未达到最大重试次数,则重试
          if (retryCount < maxRetries) {
            console.warn(`准备进行第 ${retryCount + 1} 次重试...`);
            await new Promise(resolve => setTimeout(resolve, 1000)); // 等待1秒后重试
            return await this.sendToDify(message, retryCount + 1);
          } else {
            console.warn('已达到最大重试次数,放弃重试');
            alert('未能从API响应中提取到AI回复，请查看控制台日志获取详细信息');
            return null;
          }
        }
      } catch (error) {
        console.error('调用Dify API失败:', error);
        console.error('错误详情:', {
          message: error.message,
          stack: error.stack,
          name: error.name
        });
        alert(`调用Dify API失败: ${error.message}`);
        return null;
      }
    }
  }
}
</script>

<style>
.chat-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100vw;
  height: 100vh;
  padding: 0;
  margin: 0;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

/* 深色模式样式 */
body.dark-mode .chat-container {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.chat-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.08) 0%, transparent 60%);
  animation: rotate 30s linear infinite;
}

body.dark-mode .chat-container::before {
  background: radial-gradient(circle, rgba(102, 126, 234, 0.05) 0%, transparent 60%);
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.main-panel {
  display: flex;
  width: 100%;
  height: 100%;
  max-width: 100%;
  gap: 0;
  position: relative;
  z-index: 1;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 0;
  width: 160px;
  flex-shrink: 0;
  height: 100%;
}

.conversation-sidebar {
  flex: 1;
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 0;
  box-shadow: none;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: none;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
}

body.dark-mode .conversation-sidebar {
  background-color: rgba(30, 30, 46, 0.95);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-toolbar {
  display: flex;
  gap: 8px;
  padding: 10px 12px;
  background-color: rgba(245, 247, 250, 0.95);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

body.dark-mode .sidebar-toolbar {
  background-color: rgba(25, 25, 40, 0.95);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.toolbar-btn {
  flex: 1;
  padding: 8px;
  background-color: rgba(240, 242, 245, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  color: #333;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

body.dark-mode .toolbar-btn {
  background-color: rgba(40, 40, 60, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #e0e0e0;
}

.toolbar-btn:hover {
  background-color: rgba(230, 232, 235, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

body.dark-mode .toolbar-btn:hover {
  background-color: rgba(50, 50, 70, 0.9);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.toolbar-btn.active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
  border-color: rgba(102, 126, 234, 0.5);
}

.sidebar-header {
  padding: 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

body.dark-mode .sidebar-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-header h2 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #333;
  font-weight: 600;
}

body.dark-mode .sidebar-header h2 {
  color: #e0e0e0;
}

.new-chat-btn {
  width: 100%;
  padding: 8px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.new-chat-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.new-chat-btn:active {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.new-chat-btn .icon {
  font-size: 16px;
  font-weight: bold;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.conversation-item {
  padding: 10px 12px;
  margin-bottom: 6px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  border: 1px solid transparent;
  background-color: rgba(240, 242, 245, 0.5);
}

body.dark-mode .conversation-item {
  background-color: rgba(40, 40, 60, 0.5);
}

.conversation-item:hover {
  background-color: rgba(230, 232, 235, 0.8);
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

body.dark-mode .conversation-item:hover {
  background-color: rgba(50, 50, 70, 0.8);
}

.conversation-item.active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.conversation-title {
  font-size: 12px;
  color: #333;
  font-weight: 500;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

body.dark-mode .conversation-title {
  color: #e0e0e0;
}

.conversation-time {
  font-size: 10px;
  color: #888;
}

.delete-btn {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #ff6b6b;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  display: none;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.conversation-item:hover .delete-btn {
  display: flex;
}

.delete-btn:hover {
  background-color: #ee5253;
}

.tts-controls {
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 0;
  box-shadow: none;
  padding: 12px;
  border: none;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

body.dark-mode .tts-controls {
  background-color: rgba(30, 30, 46, 0.95);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.tts-controls h2 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
  font-size: 13px;
  font-weight: 600;
}

body.dark-mode .tts-controls h2 {
  color: #e0e0e0;
}

.tts-status {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding: 10px;
  background: linear-gradient(135deg, rgba(240, 242, 245, 0.8) 0%, rgba(230, 232, 235, 0.8) 100%);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

body.dark-mode .tts-status {
  background: linear-gradient(135deg, rgba(40, 40, 60, 0.8) 0%, rgba(30, 30, 46, 0.8) 100%);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.tts-status:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.tts-status span {
  font-weight: 600;
  color: #333;
  font-size: 12px;
}

body.dark-mode .tts-status span {
  color: #e0e0e0;
}

.switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 22px;
  vertical-align: middle;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #3a3a4a;
  transition: all 0.3s ease;
  border-radius: 28px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 2px;
  bottom: 2px;
  background-color: #e0e0e0;
  transition: all 0.3s ease;
  border-radius: 50%;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

input:checked + .slider {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2), 0 0 10px rgba(102, 126, 234, 0.4);
}

input:focus + .slider {
  box-shadow: 0 0 1px #667eea, inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

input:checked + .slider:before {
  transform: translateX(18px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

.slider.round {
  border-radius: 28px;
}

.slider.round:before {
  border-radius: 50%;
}

.manual-input h3 {
  margin-top: 0;
  margin-bottom: 8px;
  color: #333;
  font-size: 12px;
  font-weight: 600;
}

body.dark-mode .manual-input h3 {
  color: #e0e0e0;
}

.tts-controls textarea {
  width: 100%;
  padding: 8px 10px;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  resize: vertical;
  font-family: inherit;
  font-size: 12px;
  transition: border-color 0.3s, box-shadow 0.3s;
  background-color: rgba(255, 255, 255, 0.8);
  color: #333;
  margin-bottom: 8px;
  box-sizing: border-box;
  min-height: 60px;
}

body.dark-mode .tts-controls textarea {
  border: 2px solid rgba(255, 255, 255, 0.1);
  background-color: rgba(30, 30, 46, 0.8);
  color: #e0e0e0;
}

.tts-controls textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.tts-buttons {
  display: flex;
  gap: 6px;
}

.tts-controls button {
  flex: 1;
  padding: 8px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  font-weight: 600;
  font-size: 12px;
}

.tts-controls button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.tts-controls button:active {
  transform: translateY(0);
}

.tts-controls button:disabled {
  background: linear-gradient(135deg, #3a3a4a 0%, #2a2a3a 100%);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.chat-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: none;
  border-radius: 0;
  box-shadow: none;
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  overflow: hidden;
}

body.dark-mode .chat-box {
  background-color: rgba(30, 30, 46, 0.95);
}

.chat-toolbar {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background-color: rgba(245, 247, 250, 0.95);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  gap: 8px;
}

body.dark-mode .chat-toolbar {
  background-color: rgba(25, 25, 40, 0.95);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.chat-toolbar .toolbar-btn {
  padding: 6px 10px;
  background-color: rgba(240, 242, 245, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  color: #333;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

body.dark-mode .chat-toolbar .toolbar-btn {
  background-color: rgba(40, 40, 60, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #e0e0e0;
}

.chat-toolbar .toolbar-btn:hover {
  background-color: rgba(230, 232, 235, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

body.dark-mode .chat-toolbar .toolbar-btn:hover {
  background-color: rgba(50, 50, 70, 0.9);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.chat-toolbar .toolbar-btn.active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
  border-color: rgba(102, 126, 234, 0.5);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background-color: rgba(245, 247, 250, 0.5);
  background-image: none;
}

body.dark-mode .chat-messages {
  background-color: rgba(25, 25, 40, 0.5);
}

.message {
  display: flex;
  margin-bottom: 6px;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  justify-content: flex-end;
}

.message.bot {
  justify-content: flex-start;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
  overflow: hidden;
}

.message.user .message-avatar {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  order: 2;
  margin-left: 8px;
}

.message-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.message.user .message-content {
  order: 1;
}

.message.bot .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  order: 1;
  margin-right: 8px;
}

.message.bot .message-content {
  order: 2;
}

.message-content {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 16px;
  word-wrap: break-word;
  word-break: break-word;
  white-space: pre-wrap;
  line-height: 1.5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  font-size: 13px;
  font-weight: 500;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
}

.message-content:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
}

.message.user .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.bot .message-content {
  background-color: rgba(240, 242, 245, 0.95);
  color: #333;
  border-bottom-left-radius: 4px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

body.dark-mode .message.bot .message-content {
  background-color: rgba(40, 40, 60, 0.95);
  color: #e0e0e0;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.message.typing .message-content {
  background-color: rgba(240, 242, 245, 0.8);
  padding: 10px 20px;
}

body.dark-mode .message.typing .message-content {
  background-color: rgba(40, 40, 60, 0.8);
}

.typing-indicator {
  display: flex;
  gap: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background-color: #667eea;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.chat-input-area {
  padding: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 10px;
  background-color: rgba(245, 247, 250, 0.8);
  backdrop-filter: blur(10px);
}

body.dark-mode .chat-input-area {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background-color: rgba(30, 30, 46, 0.8);
}

.input-wrapper {
  flex: 1;
  display: flex;
  gap: 8px;
  position: relative;
}

.chat-input-area textarea {
  flex: 1;
  padding: 10px 12px;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  resize: none;
  font-family: inherit;
  font-size: 13px;
  transition: all 0.3s ease;
  background-color: rgba(255, 255, 255, 0.9);
  color: #333;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

body.dark-mode .chat-input-area textarea {
  border: 2px solid rgba(255, 255, 255, 0.1);
  background-color: rgba(30, 30, 46, 0.9);
  color: #e0e0e0;
}

.chat-input-area textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2);
  background-color: rgba(255, 255, 255, 0.95);
}

body.dark-mode .chat-input-area textarea:focus {
  background-color: rgba(35, 35, 55, 0.95);
}

.chat-input-area button {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  font-size: 13px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.chat-input-area button:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.chat-input-area button:active {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.chat-input-area button:disabled {
  background: linear-gradient(135deg, #3a3a4a 0%, #2a2a3a 100%);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.record-btn {
  padding: 8px 14px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  font-size: 12px;
  box-shadow: 0 4px 12px rgba(240, 147, 251, 0.3);
  white-space: nowrap;
  min-width: 70px;
}

.record-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(240, 147, 251, 0.4);
}

.record-btn:active {
  transform: translateY(0);
  box-shadow: 0 4px 12px rgba(240, 147, 251, 0.3);
}

.record-btn:disabled {
  background: linear-gradient(135deg, #3a3a4a 0%, #2a2a3a 100%);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.record-btn.recording {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5253 100%);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* 美化滚动条样式 */
.conversation-list::-webkit-scrollbar {
  width: 6px;
}

.conversation-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.conversation-list::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.5);
  border-radius: 3px;
  transition: background 0.3s ease;
}

.conversation-list::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.8);
}

.chat-messages::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.5);
  border-radius: 4px;
  transition: background 0.3s ease;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.8);
}

/* 调试面板按钮样式已移至顶部工具栏，使用toolbar-btn样式 */
</style>
