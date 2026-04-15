
<template>
  <div class="debug-panel" :class="{ 'show': show }">
    <div class="debug-header">
      <h3>调试信息</h3>
      <button @click="toggleDebugPanel" class="close-btn">×</button>
    </div>

    <div class="debug-content">
      <div class="debug-section">
        <h4>调试日志</h4>
        <div class="logs-container">
          <div
            v-for="(log, index) in logs"
            :key="index"
            class="log-entry"
            :class="log.type"
          >
            <span class="log-time">{{ formatTime(log.timestamp) }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>

      <div class="debug-controls">
        <button @click="clearLogs">清除日志</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DebugPanel',
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      logs: [],
      maxLogs: 100
    }
  },
  methods: {
    toggleDebugPanel() {
      this.$emit('toggle');
    },

    addLog(log) {
      this.logs.unshift(log);
      if (this.logs.length > this.maxLogs) {
        this.logs = this.logs.slice(0, this.maxLogs);
      }
    },

    clearLogs() {
      this.logs = [];
    },

    formatTime(timestamp) {
      try {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit', 
          second: '2-digit' 
        });
      } catch (e) {
        return timestamp;
      }
    }
  }
}
</script>

<style scoped>
.debug-panel {
  position: fixed;
  right: -400px;
  top: 0;
  width: 380px;
  height: 100vh;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: -4px 0 16px rgba(0, 0, 0, 0.1);
  transition: right 0.3s ease;
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.debug-panel.show {
  right: 0;
}

body.dark-mode .debug-panel {
  background: rgba(30, 30, 46, 0.95);
  box-shadow: -4px 0 16px rgba(0, 0, 0, 0.2);
}

.debug-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

body.dark-mode .debug-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.debug-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 24px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.debug-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.debug-section {
  margin-bottom: 24px;
}

.debug-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

body.dark-mode .debug-section h4 {
  color: #e0e0e0;
}

.logs-container {
  max-height: 400px;
  overflow-y: auto;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  padding: 12px;
}

body.dark-mode .logs-container {
  background: rgba(0, 0, 0, 0.2);
}

.log-entry {
  padding: 8px;
  margin-bottom: 4px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.4;
}

.log-entry.info {
  background: rgba(102, 126, 234, 0.1);
  border-left: 3px solid #667eea;
}

.log-entry.success {
  background: rgba(40, 167, 69, 0.1);
  border-left: 3px solid #28a745;
}

.log-entry.warning {
  background: rgba(255, 193, 7, 0.1);
  border-left: 3px solid #ffc107;
}

.log-entry.error {
  background: rgba(220, 53, 69, 0.1);
  border-left: 3px solid #dc3545;
}

.log-time {
  color: #999;
  margin-right: 8px;
}

.log-message {
  color: #333;
}

body.dark-mode .log-message {
  color: #e0e0e0;
}

.debug-controls {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.debug-controls button {
  flex: 1;
  padding: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 600;
}

.debug-controls button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.debug-controls button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
