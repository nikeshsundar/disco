import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      setAuth: (user, token) => {
        localStorage.setItem('token', token);
        set({ user, token, isAuthenticated: true });
      },
      logout: () => {
        localStorage.removeItem('token');
        set({ user: null, token: null, isAuthenticated: false });
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);

interface AssessmentState {
  currentAssessmentId: number | null;
  currentQuestionIndex: number;
  answers: Record<number, any>;
  timeRemaining: number;
  setAssessment: (id: number) => void;
  setQuestion: (index: number) => void;
  saveAnswer: (questionId: number, answer: any) => void;
  clearAssessment: () => void;
}

export const useAssessmentStore = create<AssessmentState>((set) => ({
  currentAssessmentId: null,
  currentQuestionIndex: 0,
  answers: {},
  timeRemaining: 0,
  setAssessment: (id) => set({ currentAssessmentId: id, currentQuestionIndex: 0, answers: {} }),
  setQuestion: (index) => set({ currentQuestionIndex: index }),
  saveAnswer: (questionId, answer) =>
    set((state) => ({
      answers: { ...state.answers, [questionId]: answer },
    })),
  clearAssessment: () =>
    set({ currentAssessmentId: null, currentQuestionIndex: 0, answers: {}, timeRemaining: 0 }),
}));
