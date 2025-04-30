# Build stage
FROM rust:1.75-slim as builder

WORKDIR /usr/src/app

# Copy the source code
COPY . .

# Build the application
RUN cargo build --release

# Runtime stage
FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the binary from the builder stage
COPY --from=builder /usr/src/app/target/release/home /app/home

# Set environment variables
ENV PORT=3000
ENV RUST_LOG=info

# Expose the port
EXPOSE $PORT

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1

# Run the application
ENTRYPOINT ["/app/home"] 