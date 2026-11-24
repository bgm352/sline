create table if not exists public.vault_cards (
    id uuid primary key default gen_random_uuid(),
    card_name text not null,
    category text default 'Baseball',
    grade text default 'Raw',
    cert_number text,
    cost_basis numeric(10, 2) default 0,
    market_comp numeric(10, 2) not null,
    psa_offer numeric(10, 2),
    liquidity text default 'Medium' check (liquidity in ('High', 'Medium', 'Niche')),
    default_goal text default 'Balanced' check (
        default_goal in ('Balanced', 'Fast Cash', 'Max Profit', 'Zero Hassle', 'Long-Term Hold')
    ),
    storage_location text default 'Home Safe',
    created_at timestamptz default now()
);

create index if not exists idx_vault_cards_name on public.vault_cards (card_name);
