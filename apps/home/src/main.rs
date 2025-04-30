use axum::{
    routing::get,
    Router,
};
use std::net::SocketAddr;
use tower_http::trace::TraceLayer;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};
use tokio::signal;

#[tokio::main]
async fn main() {
    // Initialize tracing
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::new(
            std::env::var("RUST_LOG").unwrap_or_else(|_| "info".into()),
        ))
        .with(tracing_subscriber::fmt::layer())
        .init();

    // Build our application with routes nested under /api
    let api_router = Router::new()
        .route("/", get(handler));

    let app = Router::new()
        .nest("/api", api_router)
        .layer(TraceLayer::new_for_http());

    // Get port from environment variable or use default
    let port = std::env::var("PORT")
        .unwrap_or_else(|_| "3000".to_string())
        .parse::<u16>()
        .expect("PORT must be a valid number");

    // Run it
    let addr = SocketAddr::from(([0, 0, 0, 0], port));
    tracing::info!("listening on {}", addr);
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    
    // Create a shutdown signal
    let shutdown = signal::ctrl_c();
    
    // Run the server with graceful shutdown
    axum::serve(listener, app)
        .with_graceful_shutdown(async {
            shutdown.await.expect("failed to listen for shutdown signal");
            tracing::info!("shutting down");
        })
        .await
        .unwrap();
}

async fn handler() -> &'static str {
    "Hello, World!"
}
