// Category color mapping with similar colors for related categories
// Each category group has a base color with variations for subcategories

export interface CategoryColor {
  bg: string;
  text: string;
  border: string;
}

export interface CategoryOption {
  key: string;
  value: string;
}

// All available transaction categories
export const TRANSACTION_CATEGORIES: CategoryOption[] = [
  // Alimentação
  { key: 'food', value: 'Alimentação' },
  { key: 'food_grocery', value: 'Alimentação - Mercado' },
  { key: 'food_restaurant', value: 'Alimentação - Restaurante' },
  { key: 'food_delivery', value: 'Alimentação - Delivery' },
  // Moradia
  { key: 'housing', value: 'Moradia' },
  { key: 'housing_rent', value: 'Moradia - Aluguel' },
  { key: 'housing_condo', value: 'Moradia - Condomínio' },
  { key: 'housing_maintenance', value: 'Moradia - Manutenção' },
  // Contas
  { key: 'bill', value: 'Conta' },
  { key: 'bill_water', value: 'Conta - Água' },
  { key: 'bill_electricity', value: 'Conta - Luz' },
  { key: 'bill_gas', value: 'Conta - Gás' },
  { key: 'bill_internet', value: 'Conta - Internet' },
  { key: 'bill_phone', value: 'Conta - Celular' },
  // Transporte
  { key: 'transport', value: 'Transporte' },
  { key: 'transport_fuel', value: 'Transporte - Combustível' },
  { key: 'transport_public', value: 'Transporte - Transporte Público' },
  { key: 'transport_apps', value: 'Transporte - Aplicativos' },
  { key: 'transport_maintenance', value: 'Transporte - Manutenção' },
  // Saúde
  { key: 'health', value: 'Saúde' },
  { key: 'health_pharmacy', value: 'Saúde - Farmácia' },
  { key: 'health_appointments', value: 'Saúde - Consultas' },
  { key: 'health_exams', value: 'Saúde - Exames' },
  { key: 'health_insurance', value: 'Saúde - Plano de Saúde' },
  // Educação
  { key: 'education', value: 'Educação' },
  { key: 'education_tuition', value: 'Educação - Mensalidade' },
  { key: 'education_courses', value: 'Educação - Cursos' },
  { key: 'education_books', value: 'Educação - Livros' },
  // Financeiro
  { key: 'financial', value: 'Financeiro' },
  { key: 'credit_card', value: 'Cartão de Crédito' },
  { key: 'loans', value: 'Empréstimos / Financiamentos' },
  { key: 'taxes', value: 'Impostos e Taxas' },
  { key: 'insurance', value: 'Seguros' },
  { key: 'subscriptions', value: 'Assinaturas' },
  // Estilo de vida
  { key: 'lifestyle', value: 'Estilo de Vida' },
  { key: 'leisure', value: 'Lazer' },
  { key: 'travel', value: 'Viagens' },
  { key: 'personal_shopping', value: 'Compras Pessoais' },
  { key: 'gifts_donations', value: 'Presentes e Doações' },
  // Renda
  { key: 'income', value: 'Renda' },
  { key: 'earnings', value: 'Rendimentos' },
  { key: 'refunds', value: 'Reembolsos' },
  // Outros
  { key: 'other', value: 'Outros' },
];

// Color definitions by category group
const categoryColors: Record<string, CategoryColor> = {
  // Alimentação - Orange tones
  'food': { bg: 'bg-orange-100', text: 'text-orange-800', border: 'border-orange-300' },
  'food_grocery': { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-200' },
  'food_restaurant': { bg: 'bg-amber-100', text: 'text-amber-800', border: 'border-amber-300' },
  'food_delivery': { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-300' },

  // Moradia - Blue tones
  'housing': { bg: 'bg-blue-100', text: 'text-blue-800', border: 'border-blue-300' },
  'housing_rent': { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
  'housing_condo': { bg: 'bg-sky-100', text: 'text-sky-800', border: 'border-sky-300' },
  'housing_maintenance': { bg: 'bg-cyan-100', text: 'text-cyan-800', border: 'border-cyan-300' },

  // Contas - Slate/Gray tones
  'bill': { bg: 'bg-slate-100', text: 'text-slate-800', border: 'border-slate-300' },
  'bill_water': { bg: 'bg-slate-50', text: 'text-slate-700', border: 'border-slate-200' },
  'bill_electricity': { bg: 'bg-zinc-100', text: 'text-zinc-800', border: 'border-zinc-300' },
  'bill_gas': { bg: 'bg-stone-100', text: 'text-stone-800', border: 'border-stone-300' },
  'bill_internet': { bg: 'bg-neutral-100', text: 'text-neutral-800', border: 'border-neutral-300' },
  'bill_phone': { bg: 'bg-gray-100', text: 'text-gray-800', border: 'border-gray-300' },

  // Transporte - Indigo tones
  'transport': { bg: 'bg-indigo-100', text: 'text-indigo-800', border: 'border-indigo-300' },
  'transport_fuel': { bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200' },
  'transport_public': { bg: 'bg-violet-100', text: 'text-violet-800', border: 'border-violet-300' },
  'transport_apps': { bg: 'bg-purple-100', text: 'text-purple-700', border: 'border-purple-200' },
  'transport_maintenance': { bg: 'bg-fuchsia-100', text: 'text-fuchsia-800', border: 'border-fuchsia-300' },

  // Saúde - Red/Rose tones
  'health': { bg: 'bg-rose-100', text: 'text-rose-800', border: 'border-rose-300' },
  'health_pharmacy': { bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200' },
  'health_appointments': { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-300' },
  'health_exams': { bg: 'bg-pink-100', text: 'text-pink-800', border: 'border-pink-300' },
  'health_insurance': { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },

  // Educação - Purple tones
  'education': { bg: 'bg-purple-100', text: 'text-purple-800', border: 'border-purple-300' },
  'education_tuition': { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' },
  'education_courses': { bg: 'bg-violet-100', text: 'text-violet-800', border: 'border-violet-300' },
  'education_books': { bg: 'bg-fuchsia-50', text: 'text-fuchsia-700', border: 'border-fuchsia-200' },

  // Financeiro - Emerald/Teal tones
  'financial': { bg: 'bg-emerald-100', text: 'text-emerald-800', border: 'border-emerald-300' },
  'credit_card': { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  'loans': { bg: 'bg-teal-100', text: 'text-teal-800', border: 'border-teal-300' },
  'taxes': { bg: 'bg-cyan-100', text: 'text-cyan-800', border: 'border-cyan-300' },
  'insurance': { bg: 'bg-teal-50', text: 'text-teal-700', border: 'border-teal-200' },
  'subscriptions': { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-300' },

  // Estilo de vida - Pink/Magenta tones
  'lifestyle': { bg: 'bg-pink-100', text: 'text-pink-800', border: 'border-pink-300' },
  'leisure': { bg: 'bg-pink-50', text: 'text-pink-700', border: 'border-pink-200' },
  'travel': { bg: 'bg-fuchsia-100', text: 'text-fuchsia-800', border: 'border-fuchsia-300' },
  'personal_shopping': { bg: 'bg-rose-100', text: 'text-rose-700', border: 'border-rose-200' },
  'gifts_donations': { bg: 'bg-magenta-100 bg-pink-100', text: 'text-pink-800', border: 'border-pink-300' },

  // Renda - Green tones (positive)
  'income': { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-300' },
  'earnings': { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200' },
  'refunds': { bg: 'bg-lime-100', text: 'text-lime-800', border: 'border-lime-300' },

  // Outros - Neutral
  'other': { bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-300' },
};

// Default color for unknown categories
const defaultColor: CategoryColor = {
  bg: 'bg-gray-100',
  text: 'text-gray-600',
  border: 'border-gray-300',
};

/**
 * Get the color classes for a category
 * @param categoryKey - The category key (e.g., 'food_grocery', 'education_tuition')
 * @returns CategoryColor object with bg, text, and border classes
 */
export function getCategoryColor(categoryKey: string | undefined | null): CategoryColor {
  if (!categoryKey) return defaultColor;
  
  const normalizedKey = categoryKey.toLowerCase().replace(/-/g, '_');
  return categoryColors[normalizedKey] || defaultColor;
}

/**
 * Get combined className string for a category badge
 * @param categoryKey - The category key
 * @returns Combined className string
 */
export function getCategoryClassName(categoryKey: string | undefined | null): string {
  const colors = getCategoryColor(categoryKey);
  return `${colors.bg} ${colors.text} ${colors.border}`;
}

