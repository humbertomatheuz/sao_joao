export async function onRequestGet(context) {
  try {
    // context.env.DB é o binding automático do D1 configurado no painel da Cloudflare
    const { results } = await context.env.DB.prepare(
      "SELECT banda, local, data FROM shows ORDER BY data ASC"
    ).all();

    // Formata os dados para o padrão esperado pelo index.html
    const shows = results.map(row => ({
      "Banda/Artista": row.banda,
      "Local": row.local,
      "Data": row.data
    }));

    return new Response(JSON.stringify(shows), {
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"
      }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { 
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }
}
