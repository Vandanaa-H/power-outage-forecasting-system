import React from 'react';
import { 
  HomeIcon, 
  MapIcon, 
  CloudIcon, 
  ChartBarIcon,
  CogIcon,
  NewspaperIcon,
  BeakerIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { NavLink } from 'react-router-dom';
import useStore from '../../store/useStore';
import { motion, AnimatePresence } from 'framer-motion';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Prediction Map', href: '/map', icon: MapIcon },
  { name: 'Weather Data', href: '/weather', icon: CloudIcon },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  { name: 'What-If Simulator', href: '/simulator', icon: BeakerIcon },
  { name: 'Public Advisory', href: '/advisory', icon: NewspaperIcon },
  { name: 'Settings', href: '/settings', icon: CogIcon },
];

const Sidebar = () => {
  const { sidebarOpen, setSidebarOpen } = useStore();

  return (
    <>
      {/* Mobile overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-20 bg-black bg-opacity-50 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.div
        initial={false}
        animate={{ 
          width: sidebarOpen ? 256 : 64,
          transition: { duration: 0.3, ease: 'easeInOut' }
        }}
        className={`fixed left-0 top-0 z-30 h-full bg-white border-r border-neutral-200 shadow-lg`}
      >
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex h-16 items-center justify-between px-4 border-b border-neutral-200">
            <AnimatePresence>
              {sidebarOpen && (
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="flex items-center"
                >
                  <div className="flex-shrink-0">
                    <div className="h-9 w-9 bg-gradient-to-r from-primary-600 to-primary-800 rounded-lg flex items-center justify-center">
                      <span className="text-white font-bold text-base">KP</span>
                    </div>
                  </div>
                  <div className="ml-3 leading-tight">
                    <h1 className="text-xl font-semibold text-neutral-900">
                      Karnataka Power
                    </h1>
                    <p className="text-xs text-neutral-500">Outage Forecast</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1.5 rounded-md text-neutral-500 hover:text-neutral-900 hover:bg-neutral-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {sidebarOpen ? (
                <XMarkIcon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-4 space-y-1">
            {navigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  `group flex items-center gap-3 px-3 py-2.5 text-[15px] font-medium rounded-lg transition-colors duration-200 ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-600'
                      : 'text-neutral-700 hover:bg-neutral-100 hover:text-neutral-900'
                  }`
                }
              >
                <item.icon
                  className={`flex-shrink-0 h-6 w-6 ${
                    sidebarOpen ? 'mr-3' : 'mx-auto'
                  }`}
                />
                <AnimatePresence>
                  {sidebarOpen && (
                    <motion.span
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -10 }}
                      transition={{ duration: 0.2 }}
                    >
                      {item.name}
                    </motion.span>
                  )}
                </AnimatePresence>
              </NavLink>
            ))}
          </nav>

          {/* Footer */}
          <div className="border-t border-neutral-200 p-4">
            <AnimatePresence>
              {sidebarOpen && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-xs text-neutral-500"
                >
                  <p>Karnataka Power Outage</p>
                  <p>Forecasting System v1.0</p>
                  <p className="mt-2 text-neutral-400">
                    Real-time AI predictions
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </motion.div>
    </>
  );
};

export default Sidebar;
