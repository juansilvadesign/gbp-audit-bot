'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Settings, Bell, Shield, Palette } from 'lucide-react';
import WhatsAppConfig from '@/components/WhatsAppConfig';

// Mock project for demo - in production, fetch from API
interface ProjectSettings {
  id: string;
  business_name: string;
  whatsapp_group_id?: string;
  whatsapp_enabled: boolean;
}

export default function SettingsPage() {
  const [project, setProject] = useState<ProjectSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // In production, fetch actual project settings from API
    // For demo, using mock data
    setTimeout(() => {
      setProject({
        id: 'demo-project-id',
        business_name: 'Minha Empresa',
        whatsapp_group_id: '',
        whatsapp_enabled: false,
      });
      setIsLoading(false);
    }, 500);
  }, []);

  const handleWhatsAppSave = (groupId: string, enabled: boolean) => {
    // TODO: Call API to save WhatsApp settings
    console.log('Saving WhatsApp settings:', { groupId, enabled });
    setProject((prev) =>
      prev ? { ...prev, whatsapp_group_id: groupId, whatsapp_enabled: enabled } : null
    );
  };

  if (isLoading) {
    return (
      <div className="min-h-screen p-6 lg:p-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-[var(--surface)] rounded w-1/4"></div>
          <div className="h-64 bg-[var(--surface)] rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6 lg:p-8">
      {/* Header */}
      <header className="mb-8">
        <Link
          href="/search"
          className="inline-flex items-center gap-2 text-[var(--text-muted)] hover:text-white transition-colors mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Voltar
        </Link>

        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-[var(--accent)]/20">
            <Settings className="w-6 h-6 text-[var(--accent)]" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Configurações</h1>
            <p className="text-[var(--text-muted)]">{project?.business_name}</p>
          </div>
        </div>
      </header>

      {/* Settings Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* WhatsApp Config */}
        {project && (
          <WhatsAppConfig
            projectId={project.id}
            initialGroupId={project.whatsapp_group_id}
            initialEnabled={project.whatsapp_enabled}
            onSave={handleWhatsAppSave}
          />
        )}

        {/* Notifications (placeholder) */}
        <div className="card opacity-60">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-[var(--accent)]/20">
              <Bell className="w-5 h-5 text-[var(--accent)]" />
            </div>
            <div>
              <h3 className="font-semibold">Notificações</h3>
              <p className="text-sm text-[var(--text-muted)]">Em breve</p>
            </div>
          </div>
          <p className="text-sm text-[var(--text-muted)]">
            Configurações de notificações por e-mail e push.
          </p>
        </div>

        {/* Security (placeholder) */}
        <div className="card opacity-60">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-yellow-500/20">
              <Shield className="w-5 h-5 text-yellow-500" />
            </div>
            <div>
              <h3 className="font-semibold">Segurança</h3>
              <p className="text-sm text-[var(--text-muted)]">Em breve</p>
            </div>
          </div>
          <p className="text-sm text-[var(--text-muted)]">
            Alterar senha e configurações de autenticação.
          </p>
        </div>

        {/* Theme (placeholder) */}
        <div className="card opacity-60">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-purple-500/20">
              <Palette className="w-5 h-5 text-purple-500" />
            </div>
            <div>
              <h3 className="font-semibold">Aparência</h3>
              <p className="text-sm text-[var(--text-muted)]">Em breve</p>
            </div>
          </div>
          <p className="text-sm text-[var(--text-muted)]">
            Personalizar cores e tema da interface.
          </p>
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-12 text-center text-sm text-[var(--text-muted)]">
        <p>GBP Audit Bot by <span className="gradient-text font-semibold">Juan</span> ⚡</p>
      </footer>
    </div>
  );
}
