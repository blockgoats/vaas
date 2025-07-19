import { create } from 'zustand';

interface Workspace {
  id: string;
  name: string;
  description: string;
  createdAt: string;
  memberCount: number;
  status: 'active' | 'inactive';
}

interface WorkspaceState {
  workspaces: Workspace[];
  currentWorkspace: Workspace | null;
  setWorkspaces: (workspaces: Workspace[]) => void;
  setCurrentWorkspace: (workspace: Workspace) => void;
  addWorkspace: (workspace: Workspace) => void;
  updateWorkspace: (id: string, updates: Partial<Workspace>) => void;
  deleteWorkspace: (id: string) => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  workspaces: [
    {
      id: 'ws-1',
      name: 'Analytics Team',
      description: 'Main analytics workspace for business intelligence',
      createdAt: '2024-01-15',
      memberCount: 12,
      status: 'active',
    },
    {
      id: 'ws-2',
      name: 'Marketing Dashboard',
      description: 'Marketing metrics and campaign performance',
      createdAt: '2024-01-20',
      memberCount: 8,
      status: 'active',
    },
  ],
  currentWorkspace: null,
  setWorkspaces: (workspaces) => set({ workspaces }),
  setCurrentWorkspace: (workspace) => set({ currentWorkspace: workspace }),
  addWorkspace: (workspace) =>
    set((state) => ({ workspaces: [...state.workspaces, workspace] })),
  updateWorkspace: (id, updates) =>
    set((state) => ({
      workspaces: state.workspaces.map((ws) =>
        ws.id === id ? { ...ws, ...updates } : ws
      ),
    })),
  deleteWorkspace: (id) =>
    set((state) => ({
      workspaces: state.workspaces.filter((ws) => ws.id !== id),
    })),
}));