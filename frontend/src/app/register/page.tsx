'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { MapPin, Mail, Lock, User, Loader2, AlertCircle, CheckCircle } from 'lucide-react';

export default function RegisterPage() {
  const router = useRouter();
  const { register, isAuthenticated } = useAuth();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Redirect if already authenticated
  if (isAuthenticated) {
    router.push('/');
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate password match
    if (password !== confirmPassword) {
      setError('As senhas não coincidem');
      return;
    }

    // Validate password length
    if (password.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres');
      return;
    }

    setIsLoading(true);

    try {
      await register(email, name, password);
      router.push('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao criar conta');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-[var(--rank-green)] to-[var(--accent)] flex items-center justify-center mb-4">
            <MapPin className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold">GBP Audit Bot</h1>
          <p className="text-[var(--text-muted)]">Crie sua conta</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="card space-y-5">
          {error && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-[var(--rank-red)]/10 border border-[var(--rank-red)]/30 text-[var(--rank-red)]">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-2">
              <User className="w-4 h-4 inline mr-2" />
              Nome
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Seu nome"
              required
              className="w-full px-4 py-3 rounded-lg bg-[var(--surface-hover)] border border-transparent focus:border-[var(--accent)] focus:outline-none transition-colors"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              <Mail className="w-4 h-4 inline mr-2" />
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="seu@email.com"
              required
              className="w-full px-4 py-3 rounded-lg bg-[var(--surface-hover)] border border-transparent focus:border-[var(--accent)] focus:outline-none transition-colors"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              <Lock className="w-4 h-4 inline mr-2" />
              Senha
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Mínimo 6 caracteres"
              required
              minLength={6}
              className="w-full px-4 py-3 rounded-lg bg-[var(--surface-hover)] border border-transparent focus:border-[var(--accent)] focus:outline-none transition-colors"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              <Lock className="w-4 h-4 inline mr-2" />
              Confirmar Senha
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Repita a senha"
              required
              className={`w-full px-4 py-3 rounded-lg bg-[var(--surface-hover)] border transition-colors focus:outline-none ${confirmPassword && password === confirmPassword
                ? 'border-[var(--rank-green)]'
                : confirmPassword && password !== confirmPassword
                  ? 'border-[var(--rank-red)]'
                  : 'border-transparent focus:border-[var(--accent)]'
                }`}
            />
            {confirmPassword && password === confirmPassword && (
              <p className="text-xs text-[var(--rank-green)] mt-1 flex items-center gap-1">
                <CheckCircle className="w-3 h-3" /> Senhas coincidem
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-4 rounded-lg font-semibold text-white bg-gradient-to-r from-[var(--accent)] to-[var(--rank-green)] hover:opacity-90 transition-all flex items-center justify-center gap-2 disabled:opacity-60"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Criando conta...
              </>
            ) : (
              'Criar Conta'
            )}
          </button>

          {/* Benefits */}
          <div className="p-4 rounded-lg bg-[var(--rank-green)]/10 border border-[var(--rank-green)]/30">
            <p className="text-sm font-medium text-[var(--rank-green)] mb-2">✨ Ao se cadastrar você recebe:</p>
            <ul className="text-xs text-[var(--text-muted)] space-y-1">
              <li>• 100 créditos grátis para análises</li>
              <li>• Acesso ao dashboard de rankings</li>
              <li>• Histórico completo de buscas</li>
            </ul>
          </div>

          <p className="text-center text-sm text-[var(--text-muted)]">
            Já tem uma conta?{' '}
            <Link href="/login" className="text-[var(--accent)] hover:underline">
              Fazer login
            </Link>
          </p>
        </form>

        {/* Footer */}
        <p className="text-center text-xs text-[var(--text-muted)] mt-8">
          GBP Audit Bot by <span className="gradient-text font-semibold">Juan</span> ⚡
        </p>
      </div>
    </div>
  );
}
