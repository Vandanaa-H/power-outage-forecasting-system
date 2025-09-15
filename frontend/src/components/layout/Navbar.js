import React from 'react';
import { 
  BellIcon, 
  UserCircleIcon,
  MagnifyingGlassIcon,
  WifiIcon,
  SignalIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { format } from 'date-fns';
import useStore from '../../store/useStore';
import { motion } from 'framer-motion';

const Navbar = () => {
  const { 
    sidebarOpen, 
    socketConnected, 
    lastUpdate, 
    isRealTimeEnabled,
    toggleRealTime,
    error 
  } = useStore();

  return (
    <header className="bg-white border-b border-neutral-200 shadow-sm">
      <div className="flex h-16 items-center justify-between px-6">
        {/* Left section */}
        <div className="flex items-center space-x-4">
          {/* Search */}
          <div className="relative hidden md:block">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-4 w-4 text-neutral-400" />
            </div>
            <input
              type="text"
              placeholder="Search cities, zones..."
              className="block w-64 pl-10 pr-3 py-2 border border-neutral-300 rounded-lg text-sm placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>

        {/* Right section */}
        <div className="flex items-center space-x-4">
          {/* Real-time status */}
          <div className="flex items-center space-x-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={toggleRealTime}
              className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                isRealTimeEnabled
                  ? 'bg-success-100 text-success-800 hover:bg-success-200'
                  : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
              }`}
            >
              <div className={`h-2 w-2 rounded-full ${
                socketConnected && isRealTimeEnabled ? 'bg-success-500 animate-pulse' : 'bg-neutral-400'
              }`} />
              <span>{isRealTimeEnabled ? 'Live' : 'Paused'}</span>
            </motion.button>

            {/* Connection status */}
            <div className="flex items-center space-x-1 text-xs text-neutral-500">
              {socketConnected ? (
                <WifiIcon className="h-4 w-4 text-success-500" />
              ) : (
                <SignalIcon className="h-4 w-4 text-danger-500" />
              )}
              <span className="hidden sm:inline">
                {socketConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>

          {/* Error indicator */}
          {error && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center space-x-1 px-2 py-1 bg-danger-100 text-danger-800 rounded-lg text-xs"
            >
              <ExclamationTriangleIcon className="h-4 w-4" />
              <span className="hidden sm:inline">System Alert</span>
            </motion.div>
          )}

          {/* Last update */}
          {lastUpdate && (
            <div className="hidden lg:block text-xs text-neutral-500">
              Last update: {format(new Date(lastUpdate), 'HH:mm:ss')}
            </div>
          )}

          {/* Notifications */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="relative p-2 text-neutral-400 hover:text-neutral-600 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg"
          >
            <BellIcon className="h-5 w-5" />
            <span className="absolute top-1 right-1 h-2 w-2 bg-danger-500 rounded-full animate-ping" />
            <span className="absolute top-1 right-1 h-2 w-2 bg-danger-500 rounded-full" />
          </motion.button>

          {/* User menu */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center space-x-2 p-2 text-neutral-700 hover:text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg"
          >
            <UserCircleIcon className="h-6 w-6" />
            <span className="hidden sm:block text-sm font-medium">Admin</span>
          </motion.button>
        </div>
      </div>

      {/* Mobile search */}
      <div className="md:hidden px-4 pb-3">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-4 w-4 text-neutral-400" />
          </div>
          <input
            type="text"
            placeholder="Search cities, zones..."
            className="block w-full pl-10 pr-3 py-2 border border-neutral-300 rounded-lg text-sm placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>
    </header>
  );
};

export default Navbar;
