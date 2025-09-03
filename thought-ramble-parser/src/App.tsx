import React, { useState } from 'react';
import { type ThoughtParseResponse } from '@/lib/api';
import { InputPanel } from '@/components/InputPanel';
import { OutputPanel } from '@/components/OutputPanel';
import { LLMToggle } from '@/components/LLMToggle';
import { DebugPanel } from '@/components/DebugPanel';
import { TextTriagePanel } from '@/components/TextTriagePanel';
import { Toaster } from '@/components/ui/toaster';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Brain, Github, Sparkles, Filter } from 'lucide-react';

function App() {
  const [parseResult, setParseResult] = useState<ThoughtParseResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [llmEnabled, setLlmEnabled] = useState(false);
  const [debugPanelOpen, setDebugPanelOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('parser');

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
                <h1 className="text-xl font-semibold text-gray-900">
                  Thought Rambler
                </h1>
                <p className="text-xs text-gray-600">
                  Parse & organize your stream of consciousness
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              {activeTab === 'parser' && (
                <>
                  <LLMToggle enabled={llmEnabled} onToggle={setLlmEnabled} />
                  <button
                    onClick={() => setDebugPanelOpen(!debugPanelOpen)}
                    className="px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors flex items-center gap-2"
                  >
                    <Sparkles className="w-4 h-4" />
                    Debug
                  </button>
                </>
              )}
              
              <a
                href="https://github.com/soderalohastrom/thought-rambler"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Github className="w-5 h-5 text-gray-700" />
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content with Tabs */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 mb-8">
            <TabsTrigger value="parser" className="flex items-center gap-2">
              <Brain className="w-4 h-4" />
              Thought Parser
            </TabsTrigger>
            <TabsTrigger value="triage" className="flex items-center gap-2">
              <Filter className="w-4 h-4" />
              Text Triage
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="parser">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="lg:sticky lg:top-24 lg:h-[calc(100vh-8rem)]">
                <InputPanel 
                  onParseResult={handleParseResult} 
                  isLoading={isLoading}
                  setIsLoading={setIsLoading}
                  llmEnabled={llmEnabled}
                />
              </div>
              <div>
                <OutputPanel result={parseResult} isLoading={isLoading} />
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="triage">
            <TextTriagePanel />
          </TabsContent>
        </Tabs>
      </main>

      {/* Debug Panel */}
      <DebugPanel 
        isOpen={debugPanelOpen}
        onToggle={() => setDebugPanelOpen(!debugPanelOpen)}
        result={parseResult}
      />

      <Toaster />
    </div>
  );
}

export default App;