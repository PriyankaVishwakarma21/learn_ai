export async function POST(req: Request) {
    try {
        const { question } = await req.json();

        const backendUrl = process.env.BACKENDURL;

        if (!backendUrl) {
            return Response.json(
                { error: "Backend URL is not configured" },
                { status: 500 }
            );
        }

        const response = await fetch(`${backendUrl}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ question }),
            cache: "no-store",
        });

        if (!response.ok) {
            return Response.json(
                { error: "Backend request failed" },
                { status: response.status }
            );
        }

        if (!response.body) {
            return Response.json(
                { error: "No readable stream found" },
                { status: 500 }
            );
        }

        // Forward the streaming response directly
        return new Response(response.body, {
            headers: {
                "Content-Type":
                    response.headers.get("Content-Type") ||
                    "application/octet-stream",
                "Cache-Control": "no-cache, no-transform",
            },
        });
    } catch (error) {
        console.error("Chat API error:", error);

        return Response.json(
            { error: "Internal server error" },
            { status: 500 }
        );
    }
}