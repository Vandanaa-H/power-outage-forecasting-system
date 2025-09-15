import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

function QuickActions() {
  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  const actions = [
    {
      title: 'Run Prediction',
      description: 'Generate new 24-hour forecast',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      ),
      action: 'predict',
      color: 'bg-blue-500 hover:bg-blue-600',
      link: '/map'
    },
    {
      title: 'View Map',
      description: 'Interactive risk visualization',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
        </svg>
      ),
      action: 'map',
      color: 'bg-green-500 hover:bg-green-600',
      link: '/map'
    },
    {
      title: 'Weather Update',
      description: 'Refresh weather data',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
        </svg>
      ),
      action: 'weather',
      color: 'bg-yellow-500 hover:bg-yellow-600',
      link: '/weather'
    },
    {
      title: 'What-If Analysis',
      description: 'Scenario simulation',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
        </svg>
      ),
      action: 'simulation',
      color: 'bg-purple-500 hover:bg-purple-600',
      link: '/simulator'
    },
    {
      title: 'Generate Report',
      description: 'Export system report',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      action: 'report',
      color: 'bg-indigo-500 hover:bg-indigo-600',
      link: '/analytics'
    },
    {
      title: 'Public Advisory',
      description: 'View current alerts',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
        </svg>
      ),
      action: 'advisory',
      color: 'bg-red-500 hover:bg-red-600',
      link: '/advisory'
    }
  ];

  const handleQuickAction = (action) => {
    switch (action) {
      case 'predict':
        // Trigger new prediction
        console.log('Running new prediction...');
        break;
      case 'weather':
        // Refresh weather data
        console.log('Refreshing weather data...');
        break;
      case 'report':
        // Generate report
        console.log('Generating report...');
        break;
      default:
        break;
    }
  };

  return (
    <motion.div
      variants={itemVariants}
      className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6"
    >
      <h3 className="text-lg font-semibold text-neutral-900 mb-4">Quick Actions</h3>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {actions.map((action, index) => (
          <motion.div
            key={action.action}
            variants={itemVariants}
            initial="hidden"
            animate="visible"
            transition={{ delay: index * 0.1 }}
          >
            {action.link ? (
              <Link
                to={action.link}
                className={`block p-4 rounded-lg text-white transition-colors transform hover:scale-105 ${action.color}`}
                onClick={() => handleQuickAction(action.action)}
              >
                <div className="flex items-center space-x-3">
                  <div className="text-white">{action.icon}</div>
                  <div>
                    <h4 className="font-semibold text-base">{action.title}</h4>
                    <p className="text-sm opacity-90">{action.description}</p>
                  </div>
                </div>
              </Link>
            ) : (
              <button
                onClick={() => handleQuickAction(action.action)}
                className={`w-full p-4 rounded-lg text-white transition-colors transform hover:scale-105 ${action.color}`}
              >
                <div className="flex items-center space-x-3">
                  <div className="text-white">{action.icon}</div>
                  <div className="text-left">
                    <h4 className="font-semibold text-base">{action.title}</h4>
                    <p className="text-sm opacity-90">{action.description}</p>
                  </div>
                </div>
              </button>
            )}
          </motion.div>
        ))}
      </div>

      <div className="mt-6 pt-4 border-t border-neutral-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-neutral-600">System Status</span>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-green-600 font-medium">Online</span>
          </div>
        </div>
        <div className="flex items-center justify-between text-sm mt-2">
          <span className="text-neutral-600">Last Update</span>
          <span className="text-neutral-800">{new Date().toLocaleTimeString()}</span>
        </div>
      </div>
    </motion.div>
  );
}

export default QuickActions;
