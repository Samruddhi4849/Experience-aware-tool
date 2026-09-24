"""
Tool implementations: weather, calculator, knowledge, currency.

Every tool takes an optional `simulate` argument so the dashboard can
deterministically demonstrate each failure mode without needing a
flaky real API. In LIVE MODE (CONFIG.is_live) and with simulate=None,
tools call real, free APIs when a key is configured, and fall back to
a clearly-labelled mock result otherwise.
"""
from __future__ import annotations

import random
import time
from typing import Optional

import requests

from core.config import CONFIG
from core.models import ToolResult

_SIMULATED_LATENCY = {
    "success": (150, 600),
    "timeout": (2500, 4000),
    "invalid_argument": (50, 150),
    "rate_limit": (400, 900),
    "unavailable_tool": (30, 100),
}

_SIMULATED_ERRORS = {
    "timeout": "Request timed out waiting for a response from the tool/API.",
    "invalid_argument": "Invalid argument supplied to the tool.",
    "rate_limit": "API rate limit exceeded.",
    "unavailable_tool": "The requested tool/service is currently unavailable.",
}


def _simulated_result(tool_name: str, simulate: str, output_on_success: str) -> ToolResult:
    lo, hi = _SIMULATED_LATENCY.get(simulate, (100, 500))
    latency = random.randint(lo, hi)
    if simulate == "success":
        return ToolResult(
            tool_name=tool_name,
            success=True,
            output=output_on_success,
            error_message=None,
            latency_ms=latency,
            status="success",
        )
    status = "timeout" if simulate == "timeout" else "failure"
    return ToolResult(
        tool_name=tool_name,
        success=False,
        output=None,
        error_message=_SIMULATED_ERRORS.get(simulate, "Unknown simulated error."),
        latency_ms=latency,
        status=status,
    )


# --------------------------------------------------------------------------
# Weather
# --------------------------------------------------------------------------
def get_weather(city: str, simulate: Optional[str] = None) -> ToolResult:
    if simulate:
        return _simulated_result("weather", simulate, f"Weather in {city}: 29°C, partly cloudy, humidity 68%.")

    if CONFIG.is_live and CONFIG.openweather_api_key:
        start = time.time()
        try:
            resp = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": city, "appid": CONFIG.openweather_api_key, "units": "metric"},
                timeout=6,
            )
            latency = int((time.time() - start) * 1000)
            if resp.status_code == 200:
                data = resp.json()
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                return ToolResult(
                    tool_name="weather", success=True,
                    output=f"Weather in {city}: {temp}°C, {desc}.",
                    error_message=None, latency_ms=latency, status="success",
                )
            return ToolResult(
                tool_name="weather", success=False, output=None,
                error_message=f"Weather API returned HTTP {resp.status_code}.",
                latency_ms=latency, status="failure",
            )
        except requests.RequestException as e:
            latency = int((time.time() - start) * 1000)
            return ToolResult(
                tool_name="weather", success=False, output=None,
                error_message=f"Weather API request failed: {e}",
                latency_ms=latency, status="failure",
            )

    # Demo mode / no key configured: deterministic mock
    latency = random.randint(150, 500)
    return ToolResult(
        tool_name="weather", success=True,
        output=f"[DEMO] Weather in {city}: 29°C, partly cloudy, humidity 68%.",
        error_message=None, latency_ms=latency, status="success",
    )


# --------------------------------------------------------------------------
# Calculator
# --------------------------------------------------------------------------
_ALLOWED_CHARS = set("0123456789.+-*/() ")


def calculate(expression: str, simulate: Optional[str] = None) -> ToolResult:
    if simulate:
        return _simulated_result("calculator", simulate, f"{expression} = 42")

    start = time.time()
    if not expression or not set(expression).issubset(_ALLOWED_CHARS):
        latency = int((time.time() - start) * 1000) or random.randint(20, 80)
        return ToolResult(
            tool_name="calculator", success=False, output=None,
            error_message="Invalid argument: expression contains disallowed characters.",
            latency_ms=latency, status="failure",
        )
    try:
        result = eval(expression, {"__builtins__": {}}, {})  # noqa: S307 (chars whitelisted above)
        latency = int((time.time() - start) * 1000) or random.randint(20, 120)
        return ToolResult(
            tool_name="calculator", success=True,
            output=f"{expression} = {result}",
            error_message=None, latency_ms=latency, status="success",
        )
    except Exception as e:  # noqa: BLE001
        latency = int((time.time() - start) * 1000) or random.randint(20, 80)
        return ToolResult(
            tool_name="calculator", success=False, output=None,
            error_message=f"Could not evaluate expression: {e}",
            latency_ms=latency, status="failure",
        )


# --------------------------------------------------------------------------
# Knowledge / Wikipedia
# --------------------------------------------------------------------------
def search_knowledge(query: str, simulate: Optional[str] = None) -> ToolResult:
    if simulate:
        return _simulated_result("knowledge", simulate, f"Summary for '{query}': (demo summary text).")

    start = time.time()
    try:
        resp = requests.get(
            "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.strip().replace(" ", "_"),
            timeout=6,
        )
        latency = int((time.time() - start) * 1000)
        if resp.status_code == 200:
            data = resp.json()
            extract = data.get("extract", "No summary available.")
            return ToolResult(
                tool_name="knowledge", success=True,
                output=extract, error_message=None, latency_ms=latency, status="success",
            )
        if CONFIG.is_live:
            return ToolResult(
                tool_name="knowledge", success=False, output=None,
                error_message=f"No Wikipedia page found (HTTP {resp.status_code}).",
                latency_ms=latency, status="failure",
            )
    except requests.RequestException:
        if CONFIG.is_live:
            latency = int((time.time() - start) * 1000)
            return ToolResult(
                tool_name="knowledge", success=False, output=None,
                error_message="Knowledge API request failed (no network access).",
                latency_ms=latency, status="failure",
            )

    # Demo mode (or live mode with no network reachable to Wikipedia):
    # never fail just because there's no internet -- return a deterministic mock.
    latency = random.randint(150, 450)
    return ToolResult(
        tool_name="knowledge", success=True,
        output=f"[DEMO] '{query}' is a notable topic. (Live Mode would fetch a real Wikipedia summary here.)",
        error_message=None, latency_ms=latency, status="success",
    )


# --------------------------------------------------------------------------
# Currency
# --------------------------------------------------------------------------
_DEMO_RATES = {("USD", "INR"): 83.2, ("INR", "USD"): 0.012, ("EUR", "INR"): 90.1, ("USD", "EUR"): 0.92}


def convert_currency(
    from_currency: str, to_currency: str, amount: float, simulate: Optional[str] = None
) -> ToolResult:
    from_currency, to_currency = from_currency.upper(), to_currency.upper()

    if simulate:
        return _simulated_result(
            "currency", simulate, f"{amount} {from_currency} = {amount * 83.2:.2f} {to_currency}"
        )

    if CONFIG.is_live and CONFIG.exchangerate_api_key:
        start = time.time()
        try:
            resp = requests.get(
                f"https://v6.exchangerate-api.com/v6/{CONFIG.exchangerate_api_key}/pair/"
                f"{from_currency}/{to_currency}/{amount}",
                timeout=6,
            )
            latency = int((time.time() - start) * 1000)
            data = resp.json()
            if resp.status_code == 200 and data.get("result") == "success":
                converted = data["conversion_result"]
                return ToolResult(
                    tool_name="currency", success=True,
                    output=f"{amount} {from_currency} = {converted:.2f} {to_currency}",
                    error_message=None, latency_ms=latency, status="success",
                )
            return ToolResult(
                tool_name="currency", success=False, output=None,
                error_message=data.get("error-type", "Currency API error."),
                latency_ms=latency, status="failure",
            )
        except requests.RequestException as e:
            latency = int((time.time() - start) * 1000)
            return ToolResult(
                tool_name="currency", success=False, output=None,
                error_message=f"Currency API request failed: {e}",
                latency_ms=latency, status="failure",
            )

    # Demo mode: fixed table of common pairs
    rate = _DEMO_RATES.get((from_currency, to_currency))
    latency = random.randint(150, 450)
    if rate is None:
        return ToolResult(
            tool_name="currency", success=False, output=None,
            error_message=f"[DEMO] No demo rate available for {from_currency}->{to_currency}.",
            latency_ms=latency, status="failure",
        )
    converted = amount * rate
    return ToolResult(
        tool_name="currency", success=True,
        output=f"[DEMO] {amount} {from_currency} = {converted:.2f} {to_currency}",
        error_message=None, latency_ms=latency, status="success",
    )


TOOL_FUNCTIONS = {
    "weather": get_weather,
    "calculator": calculate,
    "knowledge": search_knowledge,
    "currency": convert_currency,
}
