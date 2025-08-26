import * as React from "react"

// Simple toaster implementation for this demo
// In production, you might want to use a more robust solution like react-hot-toast

interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'info';
}

const ToastContext = React.createContext<{
  toast: (props: ToastProps) => void;
}>({ toast: () => {} });

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<(ToastProps & { id: number })[]>([]);

  const toast = React.useCallback((props: ToastProps) => {
    const id = Date.now();
    setToasts(prev => [...prev, { ...props, id }]);
    
    setTimeout(() => {
      setToasts(prev => prev.filter(toast => toast.id !== id));
    }, 5000);
  }, []);

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 space-y-2">
        {toasts.map(({ id, message, type = 'info' }) => (
          <div
            key={id}
            className={`px-4 py-2 rounded-lg shadow-lg text-white ${
              type === 'success'
                ? 'bg-green-600'
                : type === 'error'
                ? 'bg-red-600'
                : 'bg-blue-600'
            }`}
          >
            {message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  return React.useContext(ToastContext);
}

// Simple Toaster component for compatibility
export function Toaster() {
  return null; // The actual toasts are rendered by ToastProvider
}
