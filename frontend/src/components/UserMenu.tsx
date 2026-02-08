'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { User, LogOut, Zap, ChevronDown } from 'lucide-react';

export default function UserMenu() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  if (!user) return null;

  return (
    <div className="relative" ref={menuRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-[var(--surface)] hover:bg-[var(--surface-hover)] transition-colors"
      >
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[var(--accent)] to-[var(--rank-green)] flex items-center justify-center">
          <User className="w-4 h-4 text-white" />
        </div>
        <div className="hidden md:block text-left">
          <p className="text-sm font-medium truncate max-w-[120px]">{user.name}</p>
          <p className="text-xs text-[var(--text-muted)] flex items-center gap-1">
            <Zap className="w-3 h-3 text-[var(--rank-yellow)]" />
            {user.credits_balance} créditos
          </p>
        </div>
        <ChevronDown className={`w-4 h-4 text-[var(--text-muted)] transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 py-2 bg-[var(--surface)] border border-[var(--surface-hover)] rounded-xl shadow-xl z-50">
          {/* User Info */}
          <div className="px-4 py-3 border-b border-[var(--surface-hover)]">
            <p className="font-medium">{user.name}</p>
            <p className="text-sm text-[var(--text-muted)]">{user.email}</p>
          </div>

          {/* Credits */}
          <div className="px-4 py-3 border-b border-[var(--surface-hover)]">
            <div className="flex items-center justify-between">
              <span className="text-sm text-[var(--text-muted)]">Créditos</span>
              <span className="flex items-center gap-1 font-semibold">
                <Zap className="w-4 h-4 text-[var(--rank-yellow)]" />
                {user.credits_balance}
              </span>
            </div>
            <div className="mt-2 h-2 bg-[var(--surface-hover)] rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-[var(--rank-yellow)] to-[var(--rank-green)]"
                style={{ width: `${Math.min(100, user.credits_balance)}%` }}
              />
            </div>
          </div>

          {/* Actions */}
          <div className="px-2 pt-2">
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-[var(--rank-red)] hover:bg-[var(--rank-red)]/10 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span className="text-sm">Sair da conta</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
