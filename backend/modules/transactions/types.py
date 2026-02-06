from modules.base.types import TypeItem, BaseType


class TransactionCategory(BaseType):
    # Alimentação
    FOOD = TypeItem("food", value="Alimentação")
    FOOD_GROCERY = TypeItem("food_grocery", value="Alimentação - Mercado")
    FOOD_RESTAURANT = TypeItem("food_restaurant", value="Alimentação - Restaurante")
    FOOD_DELIVERY = TypeItem("food_delivery", value="Alimentação - Delivery")
    
    # Moradia
    HOUSING = TypeItem("housing", value="Moradia")
    HOUSING_RENT = TypeItem("housing_rent", value="Moradia - Aluguel")
    HOUSING_CONDO = TypeItem("housing_condo", value="Moradia - Condomínio")
    HOUSING_MAINTENANCE = TypeItem("housing_maintenance", value="Moradia - Manutenção")

    # Contas
    BILL = TypeItem("bill", value="Conta")
    BILL_WATER = TypeItem("bill_water", value="Conta - Água")
    BILL_ELECTRICITY = TypeItem("bill_electricity", value="Conta - Luz")
    BILL_GAS = TypeItem("bill_gas", value="Conta - Gás")
    BILL_INTERNET = TypeItem("bill_internet", value="Conta - Internet")
    BILL_PHONE = TypeItem("bill_phone", value="Conta - Celular")

    # Transporte
    TRANSPORT = TypeItem("transport", value="Transporte")
    TRANSPORT_FUEL = TypeItem("transport_fuel", value="Transporte - Combustível")
    TRANSPORT_PUBLIC = TypeItem("transport_public", value="Transporte - Transporte Público")
    TRANSPORT_APPS = TypeItem("transport_apps", value="Transporte - Aplicativos")
    TRANSPORT_MAINTENANCE = TypeItem("transport_maintenance", value="Transporte - Manutenção")

    # Saúde
    HEALTH = TypeItem("health", value="Saúde")
    HEALTH_PHARMACY = TypeItem("health_pharmacy", value="Saúde - Farmácia")
    HEALTH_APPOINTMENTS = TypeItem("health_appointments", value="Saúde - Consultas")
    HEALTH_EXAMS = TypeItem("health_exams", value="Saúde - Exames")
    HEALTH_INSURANCE = TypeItem("health_insurance", value="Saúde - Plano de Saúde")

    # Educação
    EDUCATION = TypeItem("education", value="Educação")
    EDUCATION_TUITION = TypeItem("education_tuition", value="Educação - Mensalidade")
    EDUCATION_COURSES = TypeItem("education_courses", value="Educação - Cursos")
    EDUCATION_BOOKS = TypeItem("education_books", value="Educação - Livros")

    # Financeiro
    FINANCIAL = TypeItem("financial", value="Financeiro")
    CREDIT_CARD = TypeItem("credit_card", value="Cartão de Crédito")
    LOANS = TypeItem("loans", value="Empréstimos / Financiamentos")
    TAXES = TypeItem("taxes", value="Impostos e Taxas")
    INSURANCE = TypeItem("insurance", value="Seguros")
    SUBSCRIPTIONS = TypeItem("subscriptions", value="Assinaturas")

    # Estilo de vida
    LIFESTYLE = TypeItem("lifestyle", value="Estilo de Vida")
    LEISURE = TypeItem("leisure", value="Lazer")
    TRAVEL = TypeItem("travel", value="Viagens")
    PERSONAL_SHOPPING = TypeItem("personal_shopping", value="Compras Pessoais")
    GIFTS_DONATIONS = TypeItem("gifts_donations", value="Presentes e Doações")

    # Renda
    INCOME = TypeItem("income", value="Renda")
    EARNINGS = TypeItem("earnings", value="Rendimentos")
    REFUNDS = TypeItem("refunds", value="Reembolsos")

    # Outros
    OTHER = TypeItem("other", value="Outros")
