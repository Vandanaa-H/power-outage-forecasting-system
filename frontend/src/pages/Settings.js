import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { apiService } from '../services/api';
import useStore from '../store/useStore';

function Settings() {
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState({
    general: {
      refreshInterval: 30,
      autoRefresh: true,
      theme: 'light',
      language: 'en',
      timezone: 'Asia/Kolkata'
    },
    notifications: {
      emailAlerts: true,
      smsAlerts: false,
      pushNotifications: true,
      alertThreshold: 'Medium',
      quietHours: {
        enabled: false,
        start: '22:00',
        end: '06:00'
      }
    },
    api: {
      weatherApiKey: '15a0ca8a767b6b47131e8433098c2430',
      refreshRate: 300,
      retryAttempts: 3,
      timeout: 30
    },
    model: {
      predictionHorizon: 24,
      confidenceThreshold: 0.7,
      retrainFrequency: 'weekly',
      featureSelection: 'auto'
    }
  });

  const [saved, setSaved] = useState(false);

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  const tabs = [
    { 
      id: 'general', 
      name: 'General', 
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      )
    },
    { 
      id: 'notifications', 
      name: 'Notifications', 
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
        </svg>
      )
    },
    { 
      id: 'api', 
      name: 'API Settings', 
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      )
    },
    { 
      id: 'model', 
      name: 'Model Config', 
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      )
    }
  ];

  const saveSettings = async () => {
    try {
      await apiService.updateSettings(settings);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  };

  const resetSettings = () => {
    setSettings({
      general: {
        refreshInterval: 30,
        autoRefresh: true,
        theme: 'light',
        language: 'en',
        timezone: 'Asia/Kolkata'
      },
      notifications: {
        emailAlerts: true,
        smsAlerts: false,
        pushNotifications: true,
        alertThreshold: 'Medium',
        quietHours: {
          enabled: false,
          start: '22:00',
          end: '06:00'
        }
      },
      api: {
        weatherApiKey: '15a0ca8a767b6b47131e8433098c2430',
        refreshRate: 300,
        retryAttempts: 3,
        timeout: 30
      },
      model: {
        predictionHorizon: 24,
        confidenceThreshold: 0.7,
        retrainFrequency: 'weekly',
        featureSelection: 'auto'
      }
    });
  };

  const updateSetting = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
  };

  const updateNestedSetting = (category, parentKey, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [parentKey]: {
          ...prev[category][parentKey],
          [key]: value
        }
      }
    }));
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Settings</h1>
          <p className="text-neutral-600 mt-1">
            Configure system preferences and operational parameters
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={resetSettings}
            className="px-4 py-2 border border-neutral-300 rounded-md text-neutral-700 hover:bg-neutral-50 transition-colors"
          >
            Reset to Defaults
          </button>
          <button
            onClick={saveSettings}
            className={`px-6 py-2 rounded-md transition-colors ${
              saved 
                ? 'bg-green-600 text-white' 
                : 'bg-primary-600 text-white hover:bg-primary-700'
            }`}
          >
            {saved ? 'Saved!' : 'Save Changes'}
          </button>
        </div>
      </motion.div>

      <div className="flex space-x-6">
        {/* Sidebar Navigation */}
        <motion.div variants={itemVariants} className="w-64 bg-white rounded-lg shadow-sm border border-neutral-200 p-4">
          <nav className="space-y-2">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center px-3 py-2 text-left rounded-md transition-colors ${
                  activeTab === tab.id
                    ? 'bg-primary-100 text-primary-700 border-primary-200'
                    : 'text-neutral-700 hover:bg-neutral-50'
                }`}
              >
                <span className="mr-3">{tab.icon}</span>
                <span className="font-medium">{tab.name}</span>
              </button>
            ))}
          </nav>
        </motion.div>

        {/* Settings Content */}
        <motion.div variants={itemVariants} className="flex-1 bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
          {activeTab === 'general' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold text-neutral-900">General Settings</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Data Refresh Interval (seconds)
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="300"
                    value={settings.general.refreshInterval}
                    onChange={(e) => updateSetting('general', 'refreshInterval', parseInt(e.target.value))}
                    className="w-full border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Theme
                  </label>
                  <select
                    value={settings.general.theme}
                    onChange={(e) => updateSetting('general', 'theme', e.target.value)}
                    className="w-full border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                    <option value="auto">Auto</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Language
                  </label>
                  <select
                    value={settings.general.language}
                    onChange={(e) => updateSetting('general', 'language', e.target.value)}
                    className="w-full border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="en">English</option>
                    <option value="hi">Hindi</option>
                    <option value="kn">Kannada</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Timezone
                  </label>
                  <select
                    value={settings.general.timezone}
                    onChange={(e) => updateSetting('general', 'timezone', e.target.value)}
                    className="w-full border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="Asia/Kolkata">Asia/Kolkata (IST)</option>
                    <option value="UTC">UTC</option>
                  </select>
                </div>
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.general.autoRefresh}
                  onChange={(e) => updateSetting('general', 'autoRefresh', e.target.checked)}
                  className="rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                />
                <label className="ml-2 text-sm text-neutral-700">Enable auto-refresh</label>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold text-neutral-900">Notification Settings</h2>
              
              <div className="space-y-4">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.notifications.emailAlerts}
                    onChange={(e) => updateSetting('notifications', 'emailAlerts', e.target.checked)}
                    className="rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                  />
                  <label className="ml-2 text-sm text-neutral-700">Email Alerts</label>
                </div>
                
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.notifications.smsAlerts}
                    onChange={(e) => updateSetting('notifications', 'smsAlerts', e.target.checked)}
                    className="rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                  />
                  <label className="ml-2 text-sm text-neutral-700">SMS Alerts</label>
                </div>
                
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.notifications.pushNotifications}
                    onChange={(e) => updateSetting('notifications', 'pushNotifications', e.target.checked)}
                    className="rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                  />
                  <label className="ml-2 text-sm text-neutral-700">Push Notifications</label>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Alert Threshold
                </label>
                <select
                  value={settings.notifications.alertThreshold}
                  onChange={(e) => updateSetting('notifications', 'alertThreshold', e.target.value)}
                  className="w-full max-w-xs border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="Low">Low Risk</option>
                  <option value="Medium">Medium Risk</option>
                  <option value="High">High Risk</option>
                  <option value="Critical">Critical Only</option>
                </select>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.notifications.quietHours.enabled}
                    onChange={(e) => updateNestedSetting('notifications', 'quietHours', 'enabled', e.target.checked)}
                    className="rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                  />
                  <label className="ml-2 text-sm text-neutral-700">Enable Quiet Hours</label>
                </div>
                
                {settings.notifications.quietHours.enabled && (
                  <div className="grid grid-cols-2 gap-4 ml-6">
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-2">Start Time</label>
                      <input
                        type="time"
                        value={settings.notifications.quietHours.start}
                        onChange={(e) => updateNestedSetting('notifications', 'quietHours', 'start', e.target.value)}
                        className="w-full border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-2">End Time</label>
                      <input
                        type="time"
                        value={settings.notifications.quietHours.end}
                        onChange={(e) => updateNestedSetting('notifications', 'quietHours', 'end', e.target.value)}
                        className="w-full border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'api' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold text-neutral-900">API Configuration</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Weather API Key
                  </label>
                  <input
                    type="password"
                    value={settings.api.weatherApiKey}
                    onChange={(e) => updateSetting('api', 'weatherApiKey', e.target.value)}
                    className="w-full border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Enter your weather API key"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Refresh Rate (seconds)
                  </label>
                  <input
                    type="number"
                    min="60"
                    max="3600"
                    value={settings.api.refreshRate}
                    onChange={(e) => updateSetting('api', 'refreshRate', parseInt(e.target.value))}
                    className="w-full border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Retry Attempts
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={settings.api.retryAttempts}
                    onChange={(e) => updateSetting('api', 'retryAttempts', parseInt(e.target.value))}
                    className="w-full border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Timeout (seconds)
                  </label>
                  <input
                    type="number"
                    min="5"
                    max="120"
                    value={settings.api.timeout}
                    onChange={(e) => updateSetting('api', 'timeout', parseInt(e.target.value))}
                    className="w-full border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>
            </div>
          )}

          {activeTab === 'model' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold text-neutral-900">Model Configuration</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Prediction Horizon (hours)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="168"
                    value={settings.model.predictionHorizon}
                    onChange={(e) => updateSetting('model', 'predictionHorizon', parseInt(e.target.value))}
                    className="w-full border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Confidence Threshold
                  </label>
                  <input
                    type="number"
                    min="0.1"
                    max="1.0"
                    step="0.1"
                    value={settings.model.confidenceThreshold}
                    onChange={(e) => updateSetting('model', 'confidenceThreshold', parseFloat(e.target.value))}
                    className="w-full border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Retrain Frequency
                  </label>
                  <select
                    value={settings.model.retrainFrequency}
                    onChange={(e) => updateSetting('model', 'retrainFrequency', e.target.value)}
                    className="w-full border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="manual">Manual</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Feature Selection
                  </label>
                  <select
                    value={settings.model.featureSelection}
                    onChange={(e) => updateSetting('model', 'featureSelection', e.target.value)}
                    className="w-full border border-neutral-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="auto">Automatic</option>
                    <option value="manual">Manual</option>
                    <option value="importance">Importance-based</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </motion.div>
  );
}

export default Settings;
