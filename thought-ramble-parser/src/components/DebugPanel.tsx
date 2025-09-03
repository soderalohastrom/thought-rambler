import React, { useState } from 'react';
import { type ThoughtParseResponse, type VerboseLog } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Bug, 
  ChevronRight, 
  ChevronDown, 
  Clock, 
  AlertCircle, 
  CheckCircle, 
  XCircle, 
  Settings,
  Database,
  Network,
  Zap,
  Eye,
  EyeOff
} from 'lucide-react';

interface DebugPanelProps {
  isOpen: boolean;
  onToggle: () => void;
  result: ThoughtParseResponse | null;
}

interface LogStepProps {
  step: string;
  isActive: boolean;
  isSuccess: boolean;
  isFailed: boolean;
  duration?: number;
  details?: any;
}

function LogStep({ step, isActive, isSuccess, isFailed, duration, details }: LogStepProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const getIcon = () => {
    if (isFailed) return <XCircle className="w-4 h-4 text-red-500" />;
    if (isSuccess) return <CheckCircle className="w-4 h-4 text-green-500" />;
    if (isActive) return <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
    return <div className="w-4 h-4 rounded-full border-2 border-gray-300" />;
  };
  
  const getStepName = (step: string) => {
    const stepNames: Record<string, string> = {
      'initialization': '🚀 Initialization',
      'preparing_request': '📝 Preparing Request',
      'sending_request': '📤 Sending Request',
      'parsing_response': '🔍 Parsing Response',
      'processing_response': '⚙️ Processing Response',
      'success': '✅ Success',
      'cloudflare_api_error': '❌ Cloudflare API Error',
      'http_error': '🌐 HTTP Error',
      'network_error': '📡 Network Error',
      'request_exception': '⚠️ Request Exception',
      'general_exception': '💥 General Exception'
    };
    
    return stepNames[step] || `📋 ${step.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}`;
  };
  
  return (
    <div className="border-l-2 border-gray-200 pl-4 pb-3">
      <div 
        className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-2 rounded"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {getIcon()}
        <span className="font-medium text-sm">{getStepName(step)}</span>
        {duration && (
          <Badge variant="secondary" className="text-xs">
            {duration.toFixed(2)}s
          </Badge>
        )}
        {details && (
          <div className="ml-auto">
            {isExpanded ? (
              <ChevronDown className="w-4 h-4 text-gray-400" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-400" />
            )}
          </div>
        )}
      </div>
      
      {isExpanded && details && (
        <div className="mt-2 ml-6 p-3 bg-gray-50 rounded text-xs">
          <pre className="whitespace-pre-wrap overflow-x-auto">
            {JSON.stringify(details, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export function DebugPanel({ isOpen, onToggle, result }: DebugPanelProps) {
  const [viewMode, setViewMode] = useState<'timeline' | 'raw' | 'summary'>('timeline');
  
  if (!result?.verbose_log && !result?.llm_details && !result?.request_info) {
    return (
      <div className="fixed top-4 right-4 z-50">
        <Button
          onClick={onToggle}
          variant="outline"
          size="sm"
          className="bg-white shadow-lg border-gray-300"
        >
          <Bug className="w-4 h-4 mr-2" />
          Debug
        </Button>
      </div>
    );
  }
  
  return (
    <>
      {/* Debug Toggle Button */}
      <div className="fixed top-4 right-4 z-50">
        <Button
          onClick={onToggle}
          variant={isOpen ? "default" : "outline"}
          size="sm"
          className="bg-white shadow-lg border-gray-300"
        >
          <Bug className="w-4 h-4 mr-2" />
          Debug
          {result?.verbose_log?.error && (
            <AlertCircle className="w-3 h-3 ml-1 text-red-500" />
          )}
        </Button>
      </div>
      
      {/* Debug Panel */}
      {isOpen && (
        <div className="fixed inset-y-0 right-0 w-96 bg-white shadow-2xl border-l border-gray-200 z-40 overflow-hidden flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <Bug className="w-5 h-5 text-blue-600" />
                LLM Debug Panel
              </h3>
              <Button
                onClick={onToggle}
                variant="ghost"
                size="sm"
              >
                <EyeOff className="w-4 h-4" />
              </Button>
            </div>
            
            {/* View Mode Selector */}
            <div className="flex gap-1">
              {(['timeline', 'raw', 'summary'] as const).map((mode) => (
                <Button
                  key={mode}
                  onClick={() => setViewMode(mode)}
                  variant={viewMode === mode ? "default" : "ghost"}
                  size="sm"
                  className="text-xs"
                >
                  {mode === 'timeline' && <Clock className="w-3 h-3 mr-1" />}
                  {mode === 'raw' && <Database className="w-3 h-3 mr-1" />}
                  {mode === 'summary' && <Zap className="w-3 h-3 mr-1" />}
                  {mode.charAt(0).toUpperCase() + mode.slice(1)}
                </Button>
              ))}
            </div>
          </div>
          
          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {viewMode === 'timeline' && result?.verbose_log && (
              <div className="space-y-2">
                <h4 className="font-medium text-sm flex items-center gap-2 mb-3">
                  <Network className="w-4 h-4" />
                  Request Timeline
                </h4>
                
                <LogStep
                  step="initialization"
                  isActive={false}
                  isSuccess={true}
                  isFailed={false}
                  details={{
                    endpoint: result.verbose_log.cloudflare_endpoint,
                    model: result.verbose_log.model,
                    input_length: result.verbose_log.input_text_length,
                    preview: result.verbose_log.input_text_preview
                  }}
                />
                
                <LogStep
                  step="preparing_request"
                  isActive={false}
                  isSuccess={!!result.verbose_log.request_prepared}
                  isFailed={result.verbose_log.request_prepared === false}
                  details={result.verbose_log.request_data}
                />
                
                <LogStep
                  step="sending_request"
                  isActive={false}
                  isSuccess={!!result.verbose_log.request_sent}
                  isFailed={!result.verbose_log.request_sent && !!result.verbose_log.error}
                  duration={result.verbose_log.request_duration}
                  details={{
                    headers: result.verbose_log.request_headers,
                    body_size: result.verbose_log.request_body_size,
                    status: result.verbose_log.response_status
                  }}
                />
                
                <LogStep
                  step="parsing_response"
                  isActive={false}
                  isSuccess={!!result.verbose_log.response_parsed}
                  isFailed={result.verbose_log.response_parsed === false}
                  details={{
                    response_size: result.verbose_log.response_body_size,
                    json_keys: result.verbose_log.response_json_keys,
                    success: result.verbose_log.response_success,
                    preview: result.verbose_log.response_text_preview
                  }}
                />
                
                <LogStep
                  step="processing_response"
                  isActive={false}
                  isSuccess={!!result.verbose_log.chunks_created}
                  isFailed={result.verbose_log.chunks_created === false}
                  details={{
                    thought_groups_count: result.verbose_log.thought_groups_count,
                    first_group: result.verbose_log.first_group_detail,
                    final_chunks: result.verbose_log.final_chunks_count || result.verbose_log.chunks_created || 0
                  }}
                />
                
                {result.verbose_log.error && (
                  <LogStep
                    step={result.verbose_log.step || 'error'}
                    isActive={false}
                    isSuccess={false}
                    isFailed={true}
                    details={{
                      error: result.verbose_log.error,
                      error_type: result.verbose_log.error_type,
                      http_code: result.verbose_log.http_error_code,
                      traceback: result.verbose_log.traceback
                    }}
                  />
                )}
              </div>
            )}
            
            {viewMode === 'summary' && (
              <div className="space-y-4">
                <h4 className="font-medium text-sm flex items-center gap-2 mb-3">
                  <Zap className="w-4 h-4" />
                  Request Summary
                </h4>
                
                {/* Request Info */}
                {result?.request_info && (
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm">Request Info</CardTitle>
                    </CardHeader>
                    <CardContent className="text-xs space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Endpoint:</span>
                        <Badge variant="secondary">{result.request_info.endpoint_used}</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Fallback:</span>
                        <Badge variant={result.request_info.fallback_occurred ? "destructive" : "default"}>
                          {result.request_info.fallback_occurred ? "Yes" : "No"}
                        </Badge>
                      </div>
                      <div className="text-gray-600">
                        <div className="font-medium mb-1">Processing Steps:</div>
                        <ul className="list-disc list-inside space-y-1 text-gray-500">
                          {result.request_info.processing_steps?.map((step, i) => (
                            <li key={i}>{step}</li>
                          ))}
                        </ul>
                      </div>
                    </CardContent>
                  </Card>
                )}
                
                {/* LLM Details */}
                {result?.llm_details && (
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm">LLM Details</CardTitle>
                    </CardHeader>
                    <CardContent className="text-xs space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Cloudflare Success:</span>
                        <Badge variant={result.llm_details.cloudflare_success ? "default" : "destructive"}>
                          {result.llm_details.cloudflare_success ? "Yes" : "No"}
                        </Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Model:</span>
                        <span className="font-mono">{result.llm_details.model_used}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Coherence Score:</span>
                        <Badge variant="secondary">{result.llm_details.coherence_score}</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">CF Processing:</span>
                        <span className="font-mono">{result.llm_details.processing_time_cloudflare?.toFixed(3)}s</span>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}
            
            {viewMode === 'raw' && (
              <div className="space-y-4">
                <h4 className="font-medium text-sm flex items-center gap-2 mb-3">
                  <Database className="w-4 h-4" />
                  Raw Data
                </h4>
                
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Verbose Log</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <pre className="text-xs bg-gray-50 p-3 rounded overflow-x-auto whitespace-pre-wrap">
                      {JSON.stringify(result?.verbose_log, null, 2)}
                    </pre>
                  </CardContent>
                </Card>
                
                {result?.llm_details && (
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm">LLM Response Details</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <pre className="text-xs bg-gray-50 p-3 rounded overflow-x-auto whitespace-pre-wrap">
                        {JSON.stringify(result.llm_details, null, 2)}
                      </pre>
                    </CardContent>
                  </Card>
                )}
                
                {result?.verbose_log?.cloudflare_response_full && (
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm">Full Cloudflare Response</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <pre className="text-xs bg-gray-50 p-3 rounded overflow-x-auto whitespace-pre-wrap">
                        {JSON.stringify(result.verbose_log.cloudflare_response_full, null, 2)}
                      </pre>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}

export default DebugPanel;