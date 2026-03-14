export default {
  async fetch(request, env, ctx) {
    return new Response("Jasper Backend Service (JS Worker) is running!", {
      headers: { "content-type": "text/plain" },
    });
  },
};
