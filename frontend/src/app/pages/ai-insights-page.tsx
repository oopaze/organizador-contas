import React, { useEffect, useState, useMemo, useCallback, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/app/components/ui/table';
import { Skeleton } from '@/app/components/ui/skeleton';
import { Badge } from '@/app/components/ui/badge';
import { Button } from '@/app/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/app/components/ui/select';
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartConfig } from '@/app/components/ui/chart';
import { Bar, BarChart, XAxis, YAxis, Pie, PieChart, Cell } from 'recharts';
import { Brain, Zap, DollarSign, AlertTriangle, Hash, Cpu, Download, FileText, MessageSquare, MessagesSquare, HelpCircle, ExternalLink, ChevronLeft, ChevronRight, X } from 'lucide-react';
import { toast } from 'sonner';

const API_BASE_URL = 'http://127.0.0.1:8000';
import {
  AICallsStats,
  EmbeddingsStats,
  AICallItem,
  AIDateFilters,
  getAICallsStats,
  getEmbeddingsStats,
  getAICalls
} from '@/services';

const CHART_COLORS = [
  'hsl(var(--chart-1))',
  'hsl(var(--chart-2))',
  'hsl(var(--chart-3))',
  'hsl(var(--chart-4))',
  'hsl(var(--chart-5))',
  '#8b5cf6',
  '#ec4899',
  '#f97316',
];

const ITEMS_PER_PAGE = 20;

export const AIInsightsPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [aiCallsStats, setAICallsStats] = useState<AICallsStats | null>(null);
  const [embeddingsStats, setEmbeddingsStats] = useState<EmbeddingsStats | null>(null);
  const [allCalls, setAllCalls] = useState<AICallItem[]>([]);
  const [visibleCount, setVisibleCount] = useState(ITEMS_PER_PAGE);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Month/Year filter ('all' means no date filter)
  const [selectedMonth, setSelectedMonth] = useState<string>(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });

  // Model filter
  const [selectedModel, setSelectedModel] = useState<string>('all');
  const [availableModels, setAvailableModels] = useState<string[]>([]);

  // Format selected month for display (e.g., "Fev 2026")
  const formatMonthDisplay = (monthValue: string) => {
    if (monthValue === 'all') return 'Todos';
    const [year, month] = monthValue.split('-').map(Number);
    const date = new Date(year, month - 1, 1);
    const label = date.toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' });
    return label.charAt(0).toUpperCase() + label.slice(1).replace('.', '');
  };

  // Get current month string
  const getCurrentMonth = () => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  };

  // Navigate to previous month
  const goToPreviousMonth = () => {
    const current = selectedMonth === 'all' ? getCurrentMonth() : selectedMonth;
    const [year, month] = current.split('-').map(Number);
    const date = new Date(year, month - 2, 1);
    setSelectedMonth(`${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`);
  };

  // Navigate to next month
  const goToNextMonth = () => {
    const current = selectedMonth === 'all' ? getCurrentMonth() : selectedMonth;
    const [year, month] = current.split('-').map(Number);
    const date = new Date(year, month, 1);
    setSelectedMonth(`${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`);
  };

  // Clear date filter
  const clearDateFilter = () => {
    setSelectedMonth('all');
  };

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setVisibleCount(ITEMS_PER_PAGE); // Reset visible count when filters change

      // Build date filters (empty if 'all' selected)
      const dateFilters: AIDateFilters = {};

      if (selectedMonth !== 'all') {
        const [year, month] = selectedMonth.split('-');
        const dueDateStart = `${selectedMonth}-01`;
        const lastDay = new Date(parseInt(year), parseInt(month), 0).getDate();
        const dueDateEnd = `${selectedMonth}-${String(lastDay).padStart(2, '0')}`;
        dateFilters.due_date_start = dueDateStart;
        dateFilters.due_date_end = dueDateEnd;
      }

      const callFilters: AIDateFilters = {
        ...dateFilters,
        model: selectedModel !== 'all' ? selectedModel : undefined,
      };

      const [aiStats, embStats, calls] = await Promise.all([
        getAICallsStats(dateFilters), // Stats always show all models for the charts
        getEmbeddingsStats(dateFilters),
        getAICalls(callFilters), // Calls filtered by model
      ]);
      setAICallsStats(aiStats);
      setEmbeddingsStats(embStats);
      setAllCalls(calls);

      // Update available models from stats
      if (aiStats?.models_stats) {
        setAvailableModels(Object.keys(aiStats.models_stats));
      }
    } catch (error) {
      toast.error('Falha ao carregar dados de IA');
    } finally {
      setLoading(false);
    }
  }, [selectedMonth, selectedModel]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Lazy loading handler
  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const target = e.target as HTMLDivElement;
    const bottom = target.scrollHeight - target.scrollTop <= target.clientHeight + 100;
    if (bottom && visibleCount < allCalls.length) {
      setVisibleCount((prev) => Math.min(prev + ITEMS_PER_PAGE, allCalls.length));
    }
  }, [visibleCount, allCalls.length]);

  const visibleCalls = useMemo(() => allCalls.slice(0, visibleCount), [allCalls, visibleCount]);

  const totalSpent = (aiCallsStats?.amount_spent.total || 0) + (embeddingsStats?.amount_spent || 0);

  const modelChartData = aiCallsStats 
    ? Object.entries(aiCallsStats.models_stats).map(([model, stats]) => ({
        model: model.replace('gemini-', '').replace('-preview', ''),
        calls: stats.count,
        tokens: stats.total_tokens,
      }))
    : [];

  const modelChartConfig: ChartConfig = {
    calls: { label: 'Chamadas', color: 'hsl(var(--chart-1))' },
    tokens: { label: 'Tokens', color: 'hsl(var(--chart-2))' },
  };

  const pieChartData = aiCallsStats
    ? Object.entries(aiCallsStats.models_stats).map(([model, stats], index) => ({
        name: model,
        value: stats.count,
        fill: CHART_COLORS[index % CHART_COLORS.length],
      }))
    : [];

  const formatCurrency = (value: number, decimals: number = 3) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value);
  };

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('pt-BR').format(value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getRelatedToInfo = (relatedTo: AICallItem['related_to']) => {
    switch (relatedTo) {
      case 'file':
        return { icon: FileText, label: 'Arquivo', color: 'text-blue-600' };
      case 'message':
        return { icon: MessageSquare, label: 'Mensagem', color: 'text-green-600' };
      case 'conversation':
        return { icon: MessagesSquare, label: 'Conversa', color: 'text-purple-600' };
      default:
        return { icon: HelpCircle, label: 'Desconhecido', color: 'text-muted-foreground' };
    }
  };

  const handleDownloadResponse = (call: AICallItem) => {
    const downloadData = {
      input: call.prompt,
      output: call.response,
    };
    const data = JSON.stringify(downloadData, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai-call-${call.id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleDownloadFile = (call: AICallItem) => {
    if (call.file_url) {
      const fullUrl = `${API_BASE_URL}${call.file_url}`;
      window.open(fullUrl, '_blank');
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <Brain className="h-8 w-8 text-purple-600" />
          <div>
            <h1 className="text-2xl font-semibold">AI Insights</h1>
            <p className="text-muted-foreground">Estatísticas de uso de IA</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}><CardContent className="p-6"><Skeleton className="h-20" /></CardContent></Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Filters */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <Brain className="h-8 w-8 text-purple-600" />
          <div>
            <h1 className="text-2xl font-semibold">AI Insights</h1>
            <p className="text-muted-foreground">Estatísticas de uso de IA</p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4">
          {/* Month Navigation */}
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={goToPreviousMonth}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm font-medium min-w-[80px] text-center">
              {formatMonthDisplay(selectedMonth)}
            </span>
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={goToNextMonth}>
              <ChevronRight className="h-4 w-4" />
            </Button>
            {selectedMonth !== 'all' && (
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-muted-foreground hover:text-foreground"
                onClick={clearDateFilter}
                title="Ver todos os períodos"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>

          <div className="h-6 w-px bg-border" />

          {/* Model Filter */}
          <Select value={selectedModel} onValueChange={setSelectedModel}>
            <SelectTrigger className="w-[180px] h-8">
              <SelectValue placeholder="Modelo" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos os modelos</SelectItem>
              {availableModels.map((model) => (
                <SelectItem key={model} value={model}>
                  {model}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Chamadas</CardTitle>
            <Zap className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(aiCallsStats?.total_calls || 0)}</div>
            <p className="text-xs text-muted-foreground mt-1">
              +{formatNumber(embeddingsStats?.total_embeddings || 0)} embeddings
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Tokens</CardTitle>
            <Hash className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(aiCallsStats?.total_tokens || 0)}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {formatNumber(aiCallsStats?.total_input_tokens || 0)} in / {formatNumber(aiCallsStats?.total_output_tokens || 0)} out
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Custo Total</CardTitle>
            <DollarSign className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{formatCurrency(totalSpent)}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Input: {formatCurrency(aiCallsStats?.amount_spent.input || 0)} / Output: {formatCurrency(aiCallsStats?.amount_spent.output || 0)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Erros</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{aiCallsStats?.total_errors || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Taxa: {aiCallsStats?.total_calls ? ((aiCallsStats.total_errors / aiCallsStats.total_calls) * 100).toFixed(1) : 0}%
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Cpu className="h-5 w-5" />
              <CardTitle>Uso por Modelo</CardTitle>
            </div>
            <CardDescription>Quantidade de chamadas por modelo de IA</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={modelChartConfig} className="h-[300px] w-full">
              <BarChart data={modelChartData} layout="vertical" margin={{ left: 10, right: 10 }}>
                <XAxis type="number" />
                <YAxis dataKey="model" type="category" width={100} tick={{ fontSize: 11 }} />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar dataKey="calls" fill="var(--color-calls)" radius={4} />
              </BarChart>
            </ChartContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              <CardTitle>Distribuição de Modelos</CardTitle>
            </div>
            <CardDescription>Proporção de uso entre modelos</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={modelChartConfig} className="h-[300px] w-full">
              <PieChart>
                <Pie
                  data={pieChartData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ name, percent }) => `${name.slice(0, 10)}... ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {pieChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <ChartTooltip content={<ChartTooltipContent />} />
              </PieChart>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>

      {/* Cost per Model */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            <CardTitle>Custo por Modelo</CardTitle>
          </div>
          <CardDescription>Detalhamento de uso e custo por modelo</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Modelo</TableHead>
                <TableHead className="text-right">Chamadas</TableHead>
                <TableHead className="text-right">Tokens Input</TableHead>
                <TableHead className="text-right">Tokens Output</TableHead>
                <TableHead className="text-right">Total Tokens</TableHead>
                <TableHead className="text-right">Custo Total</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {aiCallsStats && Object.entries(aiCallsStats.models_stats).map(([model, stats]) => (
                <TableRow key={model}>
                  <TableCell>
                    <Badge variant="outline">{model}</Badge>
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatNumber(stats.count)}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatNumber(stats.total_input_tokens)}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatNumber(stats.total_output_tokens)}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatNumber(stats.total_tokens)}
                  </TableCell>
                  <TableCell className="text-right font-mono font-bold text-green-600">
                    {formatCurrency(stats.total_spent || 0)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Recent Calls Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              <CardTitle>Chamadas Recentes</CardTitle>
            </div>
            <span className="text-sm text-muted-foreground">
              {visibleCount} de {allCalls.length} chamadas
            </span>
          </div>
          <CardDescription>Todas as chamadas de IA realizadas</CardDescription>
        </CardHeader>
        <CardContent>
          <div
            ref={scrollRef}
            onScroll={handleScroll}
            className="max-h-[500px] overflow-y-auto"
          >
            <Table>
              <TableHeader className="sticky top-0 bg-card z-10">
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Data</TableHead>
                  <TableHead>Modelo</TableHead>
                  <TableHead>Origem</TableHead>
                  <TableHead className="text-right">Tokens</TableHead>
                  <TableHead className="text-right">Custo</TableHead>
                  <TableHead className="text-center">Status</TableHead>
                  <TableHead className="text-center">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {visibleCalls.map((call) => {
                  const relatedInfo = getRelatedToInfo(call.related_to);
                  const RelatedIcon = relatedInfo.icon;

                  return (
                    <TableRow key={call.id}>
                      <TableCell className="font-mono text-muted-foreground">
                        #{call.id}
                      </TableCell>
                      <TableCell className="text-muted-foreground whitespace-nowrap">
                        {formatDate(call.created_at)}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{call.model}</Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1.5">
                          <RelatedIcon className={`h-4 w-4 ${relatedInfo.color}`} />
                          <span className="text-sm">{relatedInfo.label}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {formatNumber(call.total_tokens)}
                      </TableCell>
                      <TableCell className="text-right font-mono font-bold text-green-600">
                        {formatCurrency(call.model_prices.total, 5)}
                      </TableCell>
                      <TableCell className="text-center">
                        {call.is_error ? (
                          <Badge variant="destructive">Erro</Badge>
                        ) : (
                          <Badge className="bg-green-100 text-green-800 hover:bg-green-100">OK</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center justify-center gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDownloadResponse(call)}
                            title="Baixar input/output (JSON)"
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                          {call.related_to === 'file' && call.file_url && (
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDownloadFile(call)}
                              title="Abrir arquivo original"
                            >
                              <ExternalLink className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
            {visibleCount < allCalls.length && (
              <div className="py-4 text-center text-sm text-muted-foreground">
                Scroll para carregar mais...
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Embeddings Stats */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Hash className="h-5 w-5" />
            <CardTitle>Embeddings</CardTitle>
          </div>
          <CardDescription>Estatísticas de geração de embeddings</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-muted rounded-lg">
              <p className="text-sm text-muted-foreground">Total</p>
              <p className="text-2xl font-bold">{formatNumber(embeddingsStats?.total_embeddings || 0)}</p>
            </div>
            <div className="text-center p-4 bg-muted rounded-lg">
              <p className="text-sm text-muted-foreground">Tokens</p>
              <p className="text-2xl font-bold">{formatNumber(embeddingsStats?.total_tokens || 0)}</p>
            </div>
            <div className="text-center p-4 bg-muted rounded-lg">
              <p className="text-sm text-muted-foreground">Custo</p>
              <p className="text-2xl font-bold text-green-600">{formatCurrency(embeddingsStats?.amount_spent || 0)}</p>
            </div>
            <div className="text-center p-4 bg-muted rounded-lg">
              <p className="text-sm text-muted-foreground">Erros</p>
              <p className="text-2xl font-bold text-red-600">{embeddingsStats?.total_errors || 0}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

