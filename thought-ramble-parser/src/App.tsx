import React, { useState } from 'react';
import { type ThoughtParseResponse } from '@/lib/api';
import { InputPanel } from '@/components/InputPanel';
import { OutputPanel } from '@/components/OutputPanel';
import { Toaster } from '@/components/ui/toaster';
import { Brain, Github, Sparkles } from 'lucide-react';

function App() {
  const [parseResult, setParseResult] = useState<ThoughtParseResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleParseResult = (result: ThoughtParseResponse) => {
    setParseResult(result);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-blue-600 to-green-600 rounded-xl">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Thought Ramble Parser
                </h1>
                <p className="text-sm text-gray-600">
                  AI-powered stream-of-consciousness analysis
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1 text-sm text-gray-500">
                <Sparkles className="w-4 h-4" />
                <span>Powered by spaCy LLM</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-8rem)]">
          {/* Left Panel - Input */}
          <div className="flex flex-col">
            <InputPanel 
              onParseResult={handleParseResult}
              isLoading={isLoading}
              setIsLoading={setIsLoading}
            />
          </div>
          
          {/* Right Panel - Output */}
          <div className="flex flex-col">
            <OutputPanel 
              result={parseResult}
              isLoading={isLoading}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-auto py-6 text-center text-sm text-gray-500">
        <div className="max-w-7xl mx-auto px-4">
          <p>
            Built with React, TypeScript, and Tailwind CSS. 
            Backend powered by FastAPI and spaCy NLP.
          </p>
        </div>
      </footer>

      <Toaster />
    </div>
  );
}

export default App;
