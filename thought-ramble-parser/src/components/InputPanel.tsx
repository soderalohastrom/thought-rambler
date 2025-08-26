import React, { useState } from 'react';
import { thoughtParserAPI, type ThoughtParseResponse, type SampleRambles } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, TestTube, FileText, MessageSquare, Brain } from 'lucide-react';

interface InputPanelProps {
  onParseResult: (result: ThoughtParseResponse) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

export function InputPanel({ onParseResult, isLoading, setIsLoading }: InputPanelProps) {
  const [inputText, setInputText] = useState('');
  const [sampleData, setSampleData] = useState<SampleRambles | null>(null);
  const [error, setError] = useState<string>('');

  React.useEffect(() => {
    // Load sample data on component mount
    thoughtParserAPI.getSampleRambles()
      .then(setSampleData)
      .catch((err) => {
        console.error('Failed to load sample data:', err);
        setError('Failed to load sample data');
      });
  }, []);

  const loadSample = (size: 'small' | 'medium' | 'large') => {
    if (!sampleData) return;
    
    const sample = thoughtParserAPI.getRandomSample(sampleData[size]);
    setInputText(sample);
    setError('');
  };

  const handleProcess = async () => {
    if (!inputText.trim()) {
      setError('Please enter some text to analyze');
      return;
    }

    setError('');
    setIsLoading(true);

    try {
      const result = await thoughtParserAPI.parseThoughts({
        text: inputText.trim(),
        provider: 'openai',
        model: 'gpt-3.5-turbo'
      });
      
      onParseResult(result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to process text';
      setError(errorMessage);
      console.error('Processing error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const getSampleInfo = (size: string) => {
    switch (size) {
      case 'small': return { words: '~100-200 words', desc: 'Basic thoughts and tasks' };
      case 'medium': return { words: '~300-500 words', desc: 'Multiple topic shifts' };
      case 'large': return { words: '~800+ words', desc: 'Complex rambling session' };
      default: return { words: '', desc: '' };
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-blue-600" />
          Input Text
        </CardTitle>
        <CardDescription>
          Enter your stream-of-consciousness text or load a sample to get started
        </CardDescription>
      </CardHeader>
      
      <CardContent className="flex-1 flex flex-col gap-4">
        {/* Test Buttons */}
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-gray-700 flex items-center gap-2">
            <TestTube className="w-4 h-4" />
            Sample Data
          </h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            {(['small', 'medium', 'large'] as const).map((size) => {
              const info = getSampleInfo(size);
              return (
                <Button
                  key={size}
                  variant="outline"
                  size="sm"
                  onClick={() => loadSample(size)}
                  disabled={!sampleData}
                  className="flex-1 h-auto p-3 text-left flex flex-col items-start gap-1 hover:bg-blue-50 hover:border-blue-300"
                >
                  <span className="font-medium capitalize">{size}</span>
                  <span className="text-xs text-gray-500">{info.words}</span>
                  <span className="text-xs text-gray-400">{info.desc}</span>
                </Button>
              );
            })}
          </div>
        </div>

        {/* Text Input */}
        <div className="flex-1 flex flex-col gap-2">
          <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Stream-of-Consciousness Text
          </label>
          
          <Textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Enter your rambling thoughts here... Talk about anything that comes to mind - work concerns, daily tasks, random observations, planning ideas, or just let your mind wander freely."
            className="flex-1 min-h-[300px] resize-none text-sm leading-relaxed"
            disabled={isLoading}
          />
          
          <div className="text-xs text-gray-500 flex justify-between">
            <span>{inputText.length} characters</span>
            <span>{inputText.trim().split(/\s+/).filter(word => word.length > 0).length} words</span>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Process Button */}
        <Button 
          onClick={handleProcess}
          disabled={isLoading || !inputText.trim()}
          size="lg"
          className="w-full bg-blue-600 hover:bg-blue-700"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
              Processing...
            </>
          ) : (
            <>
              <Brain className="w-4 h-4 mr-2" />
              Parse Thoughts
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}
