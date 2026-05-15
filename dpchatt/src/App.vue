<template>
  <div class="chat-container">
    <div class="main-panel">
      <!-- 左侧边栏：对话历史 -->
      <div class="sidebar" v-if="showSidebar">
        <div class="conversation-sidebar">
          <div class="sidebar-toolbar">
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
      </div>

      <!-- 右侧：聊天框 -->
      <div class="chat-box">
        <div class="chat-toolbar">
          <button @click="toggleSidebar" :class="['toolbar-btn', { 'active': !showSidebar }]" title="切换侧边栏">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 12h18M3 6h18M3 18h18"/>
            </svg>
          </button>
          <button @click="toggleWindowTopmost" :class="['toolbar-btn', { 'active': isWindowTopmost }]" title="置顶窗口">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 19V5"/>
              <path d="M5 12l7-7 7 7"/>
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
          </div>
          <button @click="sendMessage" :disabled="!userInput.trim() || isTyping">
            发送
          </button>
        </div>
      </div>
    </div>

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
      difyApiUrl: 'http://localhost:8009',
      conversationId: null,
      userId: 'user-' + Math.random().toString(36).substring(7),
      userInput: '',
      chatHistory: [],
      isTyping: false,
      agentAvatar: 'https://images.unsplash.com/photo-1773847840210-768347cc0d23?w=700&auto=format&fit=crop&q=60&ixlib=rb-4.1.0',
      userAvatar: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=700&auto=format&fit=crop&q=60',
      isDarkMode: true,
      showDebugPanel: false,
      conversations: [],
      currentConversationId: null,
      showSidebar: true,
      isWindowTopmost: false
    }
  },
  mounted() {
    this.loadConversations();
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode !== null) {
      this.isDarkMode = JSON.parse(savedDarkMode);
      if (this.isDarkMode) {
        document.body.classList.add('dark-mode');
      }
    }
    if (this.conversations.length === 0) {
      this.createNewConversation();
    } else {
      this.switchConversation(this.conversations[0].id);
    }
  },
  methods: {
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
    saveConversations() {
      try {
        localStorage.setItem('chat_conversations', JSON.stringify(this.conversations));
      } catch (error) {
        console.error('保存对话历史失败:', error);
      }
    },
    createNewConversation() {
      const newConversation = {
        id: Date.now().toString(),
        title: '新对话',
        createdAt: new Date().toISOString(),
        messages: [],
        difyConversationId: null
      };
      this.conversations.unshift(newConversation);
      this.currentConversationId = newConversation.id;
      this.chatHistory = [];
      this.conversationId = null;
      this.saveConversations();
      this.$nextTick(() => {
        this.scrollToBottom();
      });
    },
    switchConversation(conversationId) {
      const conversation = this.conversations.find(c => c.id === conversationId);
      if (conversation) {
        this.currentConversationId = conversationId;
        this.chatHistory = [...conversation.messages];
        this.conversationId = conversation.difyConversationId || null;
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      }
    },
    deleteConversation(conversationId) {
      this.conversations = this.conversations.filter(c => c.id !== conversationId);
      this.saveConversations();
      if (this.currentConversationId === conversationId) {
        if (this.conversations.length > 0) {
          this.switchConversation(this.conversations[0].id);
        } else {
          this.createNewConversation();
        }
      }
    },
    updateCurrentConversation() {
      const conversation = this.conversations.find(c => c.id === this.currentConversationId);
      if (conversation) {
        conversation.messages = [...this.chatHistory];
        conversation.difyConversationId = this.conversationId;
        if (conversation.title === '新对话' && this.chatHistory.length > 0) {
          const firstUserMessage = this.chatHistory.find(m => m.role === 'user');
          if (firstUserMessage) {
            conversation.title = firstUserMessage.content.substring(0, 30) + (firstUserMessage.content.length > 30 ? '...' : '');
          }
        }
        this.saveConversations();
      }
    },
    formatTime(timestamp) {
      const date = new Date(timestamp);
      const now = new Date();
      if (date.toDateString() === now.toDateString()) {
        return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
      }
      const yesterday = new Date(now);
      yesterday.setDate(yesterday.getDate() - 1);
      if (date.toDateString() === yesterday.toDateString()) {
        return '昨天';
      }
      return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
    },
    toggleDarkMode() {
      this.isDarkMode = !this.isDarkMode;
      localStorage.setItem('darkMode', this.isDarkMode);
      if (this.isDarkMode) {
        document.body.classList.add('dark-mode');
      } else {
        document.body.classList.remove('dark-mode');
      }
    },
    toggleSidebar() {
      this.showSidebar = !this.showSidebar;
    },
    toggleWindowTopmost() {
      this.isWindowTopmost = !this.isWindowTopmost;
      if (window.electron) {
        window.electron.send('toggle-always-on-top', this.isWindowTopmost);
      }
    },
    async sendMessage() {
      if (!this.userInput.trim() || this.isTyping) return;
      const message = this.userInput.trim();
      this.userInput = '';
      this.chatHistory.push({ role: 'user', content: message });
      this.$nextTick(() => this.scrollToBottom());
      this.isTyping = true;
      try {
        await this.sendToDify(message);
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
    async executeCommand(command) {
      try {
        // 确保调试面板可见
        if (!this.showDebugPanel) {
          this.showDebugPanel = true;
        }

        // 等待调试面板初始化
        await this.$nextTick();

        // 记录命令执行开始
        const startTime = new Date();

        // 使用console.log作为备用日志记录方式
        console.log('========== 命令执行开始 ==========');
        console.log('原始命令:', command);
        console.log('命令长度:', command.length, '字符');
        console.log('开始时间:', startTime.toLocaleString('zh-CN'));

        // 尝试添加日志到调试面板
        if (this.$refs.debugPanel) {
          this.$refs.debugPanel.addLog({
            timestamp: startTime.toISOString(),
            type: 'info',
            message: '========== 命令执行开始 =========='
          });
        }
        
        // 记录命令详情
        if (this.$refs.debugPanel) {
          this.$refs.debugPanel.addLog({
            timestamp: startTime.toISOString(),
            type: 'info',
            message: `原始命令: ${command.length > 200 ? command.substring(0, 200) + '...' : command}`
          });
        }
        
        if (this.$refs.debugPanel) {
          this.$refs.debugPanel.addLog({
            timestamp: startTime.toISOString(),
            type: 'info',
            message: `命令长度: ${command.length} 字符`
          });
        }
        
        if (this.$refs.debugPanel) {
          this.$refs.debugPanel.addLog({
            timestamp: startTime.toISOString(),
            type: 'info',
            message: `开始时间: ${startTime.toLocaleString('zh-CN')}`
          });
        }
        
        // 执行命令 - 需要包含[ACTION:OPENCMD]标记
        const messageWithMarker = `[ACTION:OPENCMD]${command}`;
        console.log('发送到后端的消息:', messageWithMarker);

        const response = await fetch('http://localhost:8008/process_ai_message', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: messageWithMarker })
        });
        
        if (!response.ok) {
          throw new Error('CMD命令请求失败');
        }
        
        const result = await response.json();
        const endTime = new Date();
        const executionTime = (endTime - startTime) / 1000; // 转换为秒
        
        // 记录命令执行结果
        console.log('命令执行结果:', result);
        if (result.success) {
          if (this.$refs.debugPanel) {
            this.$refs.debugPanel.addLog({
              timestamp: endTime.toISOString(),
              type: 'success',
              message: '✓ 命令执行成功'
            });
          }
          
          if (result.results && result.results.length > 0) {
            result.results.forEach((item, index) => {
              console.log(`--- 执行子命令 ${index + 1}/${result.results.length} ---`);
              if (this.$refs.debugPanel) {
                this.$refs.debugPanel.addLog({
                  timestamp: endTime.toISOString(),
                  type: 'info',
                  message: `--- 执行子命令 ${index + 1}/${result.results.length} ---`
                });
              }
              
              if (item.success) {
                console.log(`✓ 子命令执行成功 (耗时: ${item.details.execution_time?.toFixed(3) || '未知'}秒)`);
                if (this.$refs.debugPanel) {
                  this.$refs.debugPanel.addLog({
                    timestamp: endTime.toISOString(),
                    type: 'success',
                    message: `✓ 子命令执行成功 (耗时: ${item.details.execution_time?.toFixed(3) || '未知'}秒)`
                  });
                }
                
                // 显示标准输出
                if (item.details.stdout) {
                  console.log(`输出: ${item.details.stdout}`);
                  if (this.$refs.debugPanel) {
                    this.$refs.debugPanel.addLog({
                      timestamp: endTime.toISOString(),
                      type: 'info',
                      message: `输出: ${item.details.stdout}`
                    });
                  }
                }
              } else {
                console.log(`✗ 子命令执行失败 (返回码: ${item.details.returncode || '未知'})`);
                if (this.$refs.debugPanel) {
                  this.$refs.debugPanel.addLog({
                    timestamp: endTime.toISOString(),
                    type: 'error',
                    message: `✗ 子命令执行失败 (返回码: ${item.details.returncode || '未知'})`
                  });
                }
                
                // 显示错误输出
                if (item.details.stderr) {
                  console.log(`错误输出: ${item.details.stderr}`);
                  if (this.$refs.debugPanel) {
                    this.$refs.debugPanel.addLog({
                      timestamp: endTime.toISOString(),
                      type: 'error',
                      message: `错误输出: ${item.details.stderr}`
                    });
                  }
                }
              }
            });
          }
          
          // 记录总执行时间
          this.$refs.debugPanel?.addLog({
            timestamp: endTime.toISOString(),
            type: 'success',
            message: `返回码: 0`
          });
          
          this.$refs.debugPanel?.addLog({
            timestamp: endTime.toISOString(),
            type: 'success',
            message: `执行耗时: ${executionTime.toFixed(3)}秒`
          });
        } else {
          this.$refs.debugPanel?.addLog({
            timestamp: endTime.toISOString(),
            type: 'error',
            message: `✗ 命令执行失败`
          });
          
          this.$refs.debugPanel?.addLog({
            timestamp: endTime.toISOString(),
            type: 'error',
            message: `返回码: ${result.results?.[0]?.details?.returncode || '未知'}`
          });
          
          this.$refs.debugPanel?.addLog({
            timestamp: endTime.toISOString(),
            type: 'error',
            message: `执行耗时: ${executionTime.toFixed(3)}秒`
          });
          
          if (result.message) {
            this.$refs.debugPanel?.addLog({
              timestamp: endTime.toISOString(),
              type: 'error',
              message: `错误信息: ${result.message}`
            });
          }
        }
        
        // 记录命令执行结束
        this.$refs.debugPanel?.addLog({
          timestamp: endTime.toISOString(),
          type: 'info',
          message: '========== 命令执行结束 =========='
        });
      } catch (error) {
        const endTime = new Date();
        const executionTime = (endTime - startTime) / 1000; // 转换为秒
        
        this.$refs.debugPanel?.addLog({
          timestamp: endTime.toISOString(),
          type: 'error',
          message: `✗ 命令执行异常: ${error.message}`
        });
        
        this.$refs.debugPanel?.addLog({
          timestamp: endTime.toISOString(),
          type: 'error',
          message: `执行耗时: ${executionTime.toFixed(3)}秒`
        });
        
        this.$refs.debugPanel?.addLog({
          timestamp: endTime.toISOString(),
          type: 'info',
          message: '========== 命令执行结束 =========='
        });
        
        alert('CMD命令执行失败，请确保命令执行服务正在运行');
      }
    },
    async getWindows() {
      try {
        console.log('正在获取窗口列表...');
        const response = await fetch('http://localhost:8020/get_windows', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: this.lastBotMessage })
        });
        if (!response.ok) {
          throw new Error('获取窗口列表请求失败');
        }
        const result = await response.json();
        console.log('窗口列表结果:', result);
        if (result.success && result.windows) {
          let windowsText = `当前打开的窗口列表 (${result.windows.length}个):\n`;
          result.windows.forEach((window, index) => {
            windowsText += `${index + 1}. ${window.title}\n`;
          });
          this.chatHistory.push({ role: 'bot', content: windowsText });
          this.$nextTick(() => this.scrollToBottom());
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
    async topWindow(windowTitle) {
      try {
        const logMessage = `正在置顶窗口: ${windowTitle}`;
        console.log(logMessage);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: logMessage
        });
        const response = await fetch('http://localhost:8020/top_window', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ window_title: windowTitle })
        });
        if (!response.ok) {
          throw new Error('置顶窗口请求失败');
        }
        const result = await response.json();
        console.log('置顶窗口结果:', result);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: `置顶窗口结果: ${JSON.stringify(result)}`
        });
        if (result.success) {
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'success',
            message: `成功置顶窗口: ${windowTitle}`
          });
        } else {
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'error',
            message: `置顶窗口失败: ${result.message || '未知错误'}`
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
    async clickButton(buttonName) {
      try {
        const logMessage = `正在点击按钮: ${buttonName}`;
        console.log(logMessage);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: logMessage
        });
        const response = await fetch('http://localhost:8023/process_clickbutton', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: `[ACTION:CLICKBUTTON]${buttonName}` })
        });
        if (!response.ok) {
          throw new Error('点击按钮请求失败');
        }
        const result = await response.json();
        console.log('点击按钮结果:', result);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: `点击按钮结果: ${JSON.stringify(result)}`
        });
        if (result.success) {
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'success',
            message: `成功点击按钮: ${buttonName}`
          });
        } else {
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'error',
            message: `点击按钮失败: ${result.message || '未知错误'}`
          });
        }
      } catch (error) {
        const errorMsg = `点击按钮错误: ${error.message}`;
        console.error(errorMsg);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'error',
          message: errorMsg
        });
        alert('点击按钮失败，请确保按钮点击服务正在运行');
      }
    },
    async sendQQMessage(friendName, messageContent) {
      try {
        const logMessage = `正在发送QQ消息给 ${friendName}: ${messageContent}`;
        console.log(logMessage);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: logMessage
        });
        const response = await fetch('http://localhost:8021/send_message', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            message: `[ACTION:SELECTFRIEND_SENDMESSAGE]${friendName}|${messageContent}`,
            delay: 0
          })
        });
        if (!response.ok) {
          throw new Error('发送QQ消息请求失败');
        }
        const result = await response.json();
        console.log('发送QQ消息结果:', result);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: `发送QQ消息结果: ${JSON.stringify(result)}`
        });
        if (result.success) {
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'success',
            message: `成功发送QQ消息给 ${friendName}`
          });
        } else {
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'error',
            message: `发送QQ消息失败: ${result.message || '未知错误'}`
          });
        }
      } catch (error) {
        const errorMsg = `发送QQ消息错误: ${error.message}`;
        console.error(errorMsg);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'error',
          message: errorMsg
        });
        alert('发送QQ消息失败，请确保QQ消息服务正在运行');
      }
    },
    async sendQQFile(friendName, filePath) {
      try {
        const logMessage = `正在发送QQ文件给 ${friendName}: ${filePath}`;
        console.log(logMessage);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: logMessage
        });
        const response = await fetch('http://localhost:8025/send_qq_file', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            message: `[ACTION:SELECTFRIEND_SENDFILE]${friendName}|${filePath}`
          })
        });
        if (!response.ok) {
          throw new Error('发送QQ文件请求失败');
        }
        const result = await response.json();
        console.log('发送QQ文件结果:', result);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'info',
          message: `发送QQ文件结果: ${JSON.stringify(result)}`
        });
        if (result.success) {
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'success',
            message: `成功发送QQ文件给 ${friendName}`
          });
        } else {
          this.$refs.debugPanel?.addLog({
            timestamp: new Date().toISOString(),
            type: 'error',
            message: `发送QQ文件失败: ${result.message || '未知错误'}`
          });
        }
      } catch (error) {
        const errorMsg = `发送QQ文件错误: ${error.message}`;
        console.error(errorMsg);
        this.$refs.debugPanel?.addLog({
          timestamp: new Date().toISOString(),
          type: 'error',
          message: errorMsg
        });
        alert('发送QQ文件失败，请确保QQ文件服务正在运行');
      }
    },
    async sendToDify(message, retryCount = 0) {
      const maxRetries = 2;
      try {
        console.log('发送消息到Dify代理API:', message);
        const response = await fetch(`${this.difyApiUrl}/chat-messages`, {
          method: 'POST',
          headers: {
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
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`API请求失败: ${response.status} - ${response.statusText} ` + errorText);
        }
        const botMessageIndex = this.chatHistory.length;
        this.chatHistory.push({ role: 'bot', content: '' });
        this.$nextTick(() => this.scrollToBottom());
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let aiResponse = '';
        let conversationId = '';
        let isReading = true;
        let lastUpdateTime = 0;
        const updateInterval = 50;
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
              if (dataStr === '[DONE]') continue;
              try {
                const data = JSON.parse(dataStr);
                if (data.conversation_id) {
                  conversationId = data.conversation_id;
                  this.conversationId = conversationId;
                }
                if (data.event === 'message' || data.event === 'agent_message') {
                  if (data.answer) {
                    aiResponse += data.answer;
                    const now = Date.now();
                    if (now - lastUpdateTime >= updateInterval) {
                      this.chatHistory[botMessageIndex].content = aiResponse;
                      this.$nextTick(() => this.scrollToBottom());
                      lastUpdateTime = now;
                    }
                  }
                } else if (data.event === 'workflow_finished' || data.event === 'workflow_run') {
                  if (data.outputs) {
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
        if (aiResponse) {
          this.chatHistory[botMessageIndex].content = aiResponse;
          this.$nextTick(() => this.scrollToBottom());
          console.log('AI回复:', aiResponse);
          this.lastBotMessage = aiResponse;
          let displayResponse = aiResponse;
          let speakResponse = aiResponse;
          const actions = [];

          // 新的方式：先找出所有 ACTION 标记的位置，然后提取完整内容直到下一个 [ACTION:
          const actionRegex = /\[ACTION:(READLOG|NOWWINDOWS|TOPWINDOWS|OPENCMD|CLICKBUTTON|SELECTFRIEND_SENDMESSAGE|SELECTFRIEND_SENDFILE)\]/g;
          let match;
          const actionMatches = [];

          while ((match = actionRegex.exec(aiResponse)) !== null) {
            const actionType = match[1];
            const startIndex = match.index;
            const markerEndIndex = startIndex + match[0].length;
            
            // 查找下一个 [ACTION: 的位置
            const remaining = aiResponse.slice(markerEndIndex);
            const nextActionMatch = remaining.match(/\[ACTION:/);
            
            let endIndex;
            if (nextActionMatch) {
              // 有下一个 ACTION，取到它之前
              endIndex = markerEndIndex + nextActionMatch.index;
            } else {
              // 没有下一个 ACTION，取到字符串末尾
              endIndex = aiResponse.length;
            }
            
            // 提取完整内容
            const fullMatch = aiResponse.slice(startIndex, endIndex);
            const content = fullMatch.slice(match[0].length); // 去掉标记后的内容
            
            actionMatches.push({
              type: actionType,
              fullMatch: fullMatch,
              content: content.trim()
            });
          }

          // 处理匹配到的所有动作
          for (const action of actionMatches) {
            const actionType = action.type;
            const fullMatch = action.fullMatch;
            const content = action.content;
            
            switch (actionType) {
              case 'NOWWINDOWS':
                actions.push({ type: 'NOWWINDOWS', action: () => this.getWindows() });
                speakResponse = speakResponse.replace(fullMatch, '').trim();
                break;
              case 'TOPWINDOWS':
                if (content) {
                  actions.push({ type: 'TOPWINDOWS', action: () => this.topWindow(content) });
                  speakResponse = speakResponse.replace(fullMatch, '').trim();
                }
                break;
              case 'OPENCMD':
                if (content) {
                  actions.push({ type: 'OPENCMD', action: () => this.executeCommand(content) });
                  speakResponse = speakResponse.replace(fullMatch, '').trim();
                }
                break;
              case 'CLICKBUTTON':
                if (content) {
                  actions.push({ type: 'CLICKBUTTON', action: () => this.clickButton(content) });
                  speakResponse = speakResponse.replace(fullMatch, '').trim();
                }
                break;
              case 'READLOG':
                console.log('检测到读取调试日志指令');
                const debugPanel = this.$refs.debugPanel;
                if (debugPanel && debugPanel.logs && debugPanel.logs.length > 0) {
                  const logsContent = debugPanel.logs.map(log => {
                    const time = this.formatTime(log.timestamp);
                    return `${time} ${log.message}`;
                  }).join('\n');
                  setTimeout(() => {
                    this.userInput = logsContent;
                    this.$nextTick(() => {
                      const textarea = document.querySelector('.chat-input-area textarea');
                      if (textarea) {
                        textarea.focus();
                        textarea.setSelectionRange(textarea.value.length, textarea.value.length);
                        textarea.dispatchEvent(new Event('input', { bubbles: true }));
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
                speakResponse = speakResponse.replace(fullMatch, '').trim();
                break;
              case 'SELECTFRIEND_SENDMESSAGE': {
                const parts = content.split('|');
                if (parts.length >= 2) {
                  const friendName = parts[0].trim();
                  const messageContent = parts.slice(1).join('|').trim();
                  actions.push({
                    type: 'SELECTFRIEND_SENDMESSAGE',
                    action: () => this.sendQQMessage(friendName, messageContent)
                  });
                  speakResponse = speakResponse.replace(fullMatch, '').trim();
                }
                break;
              }
              case 'SELECTFRIEND_SENDFILE': {
                const parts = content.split('|');
                if (parts.length >= 2) {
                  const friendName = parts[0].trim();
                  const filePath = parts.slice(1).join('|').trim();
                  actions.push({
                    type: 'SELECTFRIEND_SENDFILE',
                    action: () => this.sendQQFile(friendName, filePath)
                  });
                  speakResponse = speakResponse.replace(fullMatch, '').trim();
                }
                break;
              }
            }
          }
          
          // 对操作进行排序，确保TOPWINDOWS在CLICKBUTTON之前执行
          const sortedActions = [...actions].sort((a, b) => {
            if (a.type === 'TOPWINDOWS' && b.type === 'CLICKBUTTON') return -1;
            if (a.type === 'CLICKBUTTON' && b.type === 'TOPWINDOWS') return 1;
            if ((a.type === 'SELECTFRIEND_SENDMESSAGE' || a.type === 'SELECTFRIEND_SENDFILE') && b.type === 'CLICKBUTTON') return -1;
            if (a.type === 'CLICKBUTTON' && (b.type === 'SELECTFRIEND_SENDMESSAGE' || b.type === 'SELECTFRIEND_SENDFILE')) return 1;
            return 0;
          });
          
          for (const action of sortedActions) {
            console.log(`正在执行动作: ${action.type}`);
            await action.action();
            await new Promise(resolve => setTimeout(resolve, 300));
          }
          this.updateCurrentConversation();
          return displayResponse;
        } else {
          console.warn('未能从API响应中提取到AI回复');
          if (retryCount < maxRetries) {
            console.warn(`准备进行第 ${retryCount + 1} 次重试...`);
            await new Promise(resolve => setTimeout(resolve, 1000));
            return await this.sendToDify(message, retryCount + 1);
          } else {
            alert('未能从API响应中提取到AI回复，请查看控制台日志获取详细信息');
            return null;
          }
        }
      } catch (error) {
        console.error('调用Dify API失败:', error);
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
  z-index: 9999 !important;
}

body.dark-mode .chat-container {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.chat-container.always-on-top {
  z-index: 9999 !important;
  position: fixed !important;
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
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
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
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.8);
}
</style>