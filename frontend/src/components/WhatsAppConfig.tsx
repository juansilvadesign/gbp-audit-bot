'use client';

import { useState } from 'react';
import { MessageCircle, Send, CheckCircle, XCircle, Loader2 } from 'lucide-react';

interface WhatsAppConfigProps {
  projectId: string;
  initialGroupId?: string;
  initialEnabled?: boolean;
  onSave?: (groupId: string, enabled: boolean) => void;
}

export default function WhatsAppConfig({
  projectId,
  initialGroupId = '',
  initialEnabled = false,
  onSave,
}: WhatsAppConfigProps) {
  const [groupId, setGroupId] = useState(initialGroupId);
  const [enabled, setEnabled] = useState(initialEnabled);
  const [isSaving, setIsSaving] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // Call parent handler or API directly
      if (onSave) {
        onSave(groupId, enabled);
      }
      // TODO: Add API call to update project WhatsApp settings
    } finally {
      setIsSaving(false);
    }
  };

  const handleTest = async () => {
    if (!groupId) {
      setTestResult({ success: false, message: 'Configure o ID do grupo primeiro' });
      return;
    }

    setIsTesting(true);
    setTestResult(null);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/reports/whatsapp/test/${projectId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setTestResult({ success: true, message: 'Mensagem de teste enviada com sucesso!' });
      } else {
        const data = await response.json();
        setTestResult({ success: false, message: data.detail || 'Falha ao enviar mensagem' });
      }
    } catch (error) {
      setTestResult({ success: false, message: 'Erro de conexão com o servidor' });
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 rounded-lg bg-[#25D366]/20">
          <MessageCircle className="w-5 h-5 text-[#25D366]" />
        </div>
        <div>
          <h3 className="font-semibold">WhatsApp</h3>
          <p className="text-sm text-[var(--text-muted)]">Relatórios semanais automáticos</p>
        </div>
      </div>

      {/* Enable toggle */}
      <div className="flex items-center justify-between mb-4 p-3 rounded-lg bg-[var(--surface-hover)]">
        <span className="text-sm">Envio automático toda segunda-feira</span>
        <button
          onClick={() => setEnabled(!enabled)}
          className={`relative w-12 h-6 rounded-full transition-colors ${enabled ? 'bg-[#25D366]' : 'bg-gray-600'
            }`}
        >
          <span
            className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${enabled ? 'left-7' : 'left-1'
              }`}
          />
        </button>
      </div>

      {/* Group ID input */}
      <div className="mb-4">
        <label className="block text-sm text-[var(--text-muted)] mb-2">
          ID do Grupo (JID)
        </label>
        <input
          type="text"
          value={groupId}
          onChange={(e) => setGroupId(e.target.value)}
          placeholder="Ex: 5511999999999@g.us"
          className="w-full px-4 py-2 rounded-lg bg-[var(--surface-hover)] border border-[var(--surface-hover)] focus:border-[var(--accent)] focus:outline-none transition-colors"
        />
        <p className="text-xs text-[var(--text-muted)] mt-1">
          Formato: número + @g.us para grupos
        </p>
      </div>

      {/* Test result */}
      {testResult && (
        <div
          className={`flex items-center gap-2 mb-4 p-3 rounded-lg ${testResult.success
              ? 'bg-green-500/20 text-green-400'
              : 'bg-red-500/20 text-red-400'
            }`}
        >
          {testResult.success ? (
            <CheckCircle className="w-4 h-4" />
          ) : (
            <XCircle className="w-4 h-4" />
          )}
          <span className="text-sm">{testResult.message}</span>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={handleTest}
          disabled={isTesting || !groupId}
          className="flex-1 py-2 px-4 rounded-lg bg-[var(--surface-hover)] hover:bg-[var(--surface)] transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {isTesting ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
          <span>Enviar Teste</span>
        </button>
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="flex-1 py-2 px-4 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent)]/80 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {isSaving ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <CheckCircle className="w-4 h-4" />
          )}
          <span>Salvar</span>
        </button>
      </div>
    </div>
  );
}
