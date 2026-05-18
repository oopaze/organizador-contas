from django.db import models
from modules.base.models import TimedModel


class MCPOAuthClient(TimedModel):
    client_id = models.CharField(max_length=64, unique=True)
    client_secret_hash = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    redirect_uris = models.JSONField(default=list)
    user = models.ForeignKey(
        "userdata.User", on_delete=models.CASCADE,
        null=True, blank=True, related_name="mcp_oauth_clients",
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.client_id[:12]}...)"


class MCPAuthorizationCode(TimedModel):
    code = models.CharField(max_length=128, unique=True)
    client = models.ForeignKey(MCPOAuthClient, on_delete=models.CASCADE)
    user = models.ForeignKey("userdata.User", on_delete=models.CASCADE)
    redirect_uri = models.CharField(max_length=512)
    code_challenge = models.CharField(max_length=128)
    code_challenge_method = models.CharField(max_length=16, default="S256")
    scope = models.CharField(max_length=128, default="mcp:read")
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["code"])]


class MCPAccessToken(TimedModel):
    token_hash = models.CharField(max_length=64, unique=True)
    client = models.ForeignKey(MCPOAuthClient, on_delete=models.CASCADE)
    user = models.ForeignKey("userdata.User", on_delete=models.CASCADE)
    scope = models.CharField(max_length=128, default="mcp:read")
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["token_hash"])]
