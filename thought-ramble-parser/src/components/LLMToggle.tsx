import React from 'react';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Sparkles, Brain } from 'lucide-react';

interface LLMToggleProps {
  enabled: boolean;
  onToggle: (enabled: boolean) => void;
  isProcessing?: boolean;
  className?: string;
}

export function LLMToggle({ enabled, onToggle, isProcessing = false, className = '' }: LLMToggleProps) {
  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      <div className="flex items-center space-x-2">
        {enabled ? (
          <Sparkles className="h-4 w-4 text-purple-500" />
        ) : (
          <Brain className="h-4 w-4 text-gray-500" />
        )}
        <Label 
          htmlFor="llm-toggle" 
          className={`text-sm font-medium cursor-pointer ${
            isProcessing ? 'text-gray-400' : enabled ? 'text-purple-700' : 'text-gray-600'
          }`}
        >
          Gemma LLM Enhancement
        </Label>
      </div>
      
      <Switch
        id="llm-toggle"
        checked={enabled}
        onCheckedChange={onToggle}
        disabled={isProcessing}
        className="data-[state=checked]:bg-purple-600"
      />
      
      <Badge 
        variant={enabled ? "default" : "secondary"}
        className={`text-xs ${
          enabled 
            ? 'bg-purple-100 text-purple-800 hover:bg-purple-200' 
            : 'bg-gray-100 text-gray-600'
        }`}
      >
        {enabled ? 'ON' : 'OFF'}
      </Badge>
      
      {isProcessing && enabled && (
        <div className="flex items-center space-x-1">
          <div className="animate-spin rounded-full h-3 w-3 border-2 border-purple-300 border-t-purple-600"></div>
          <span className="text-xs text-purple-600">Processing...</span>
        </div>
      )}
    </div>
  );
}

interface LLMStatusProps {
  isEnhanced: boolean;
  processingTime: number;
  totalChunks: number;
  originalChunks?: number;
}

export function LLMStatus({ isEnhanced, processingTime, totalChunks, originalChunks }: LLMStatusProps) {
  return (
    <div className="flex items-center space-x-4 text-sm text-gray-600">
      <div className="flex items-center space-x-1">
        <span>Mode:</span>
        <Badge 
          variant={isEnhanced ? "default" : "secondary"}
          className={`text-xs ${
            isEnhanced 
              ? 'bg-purple-100 text-purple-800' 
              : 'bg-blue-100 text-blue-800'
          }`}
        >
          {isEnhanced ? 'LLM Enhanced' : 'Basic spaCy'}
        </Badge>
      </div>
      
      <div className="flex items-center space-x-1">
        <span>Processing:</span>
        <span className="font-mono text-xs">
          {processingTime.toFixed(2)}s
        </span>
      </div>
      
      <div className="flex items-center space-x-1">
        <span>Chunks:</span>
        <span className="font-mono text-xs">
          {totalChunks}
          {originalChunks && originalChunks !== totalChunks && (
            <span className="text-purple-600"> (merged from {originalChunks})</span>
          )}
        </span>
      </div>
    </div>
  );
}

export default LLMToggle;