#!/usr/bin/env python3
"""
Performance Metrics Analyzer for Pipecat Bot Logs

Parses bot logs and extracts TTFB metrics, token usage, and processing times.
Provides summary statistics and identifies performance bottlenecks.

Usage:
    python analyze_metrics.py bot.log
    
    Or pipe logs directly:
    uv run bot.py 2>&1 | python analyze_metrics.py -
"""

import re
import sys
from collections import defaultdict
from statistics import mean, median, stdev


def parse_ttfb(line):
    """Extract TTFB metrics from log line."""
    match = re.search(r"(\w+Service)#\d+ TTFB: ([\d.]+)", line)
    if match:
        service = match.group(1)
        ttfb = float(match.group(2)) * 1000  # Convert to ms
        return service, ttfb
    return None, None


def parse_tokens(line):
    """Extract token usage from log line."""
    match = re.search(r"prompt tokens: (\d+), completion tokens: (\d+)", line)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None


def parse_processing_time(line):
    """Extract processing time from log line."""
    match = re.search(r"(\w+Service)#\d+ processing time: ([\d.]+)", line)
    if match:
        service = match.group(1)
        proc_time = float(match.group(2)) * 1000  # Convert to ms
        return service, proc_time
    return None, None


def analyze_logs(log_file):
    """Analyze log file and extract metrics."""
    ttfb_metrics = defaultdict(list)
    processing_metrics = defaultdict(list)
    token_usage = []
    
    try:
        if log_file == '-':
            lines = sys.stdin
        else:
            lines = open(log_file, 'r', encoding='utf-8')
        
        for line in lines:
            # Parse TTFB
            service, ttfb = parse_ttfb(line)
            if service and ttfb:
                ttfb_metrics[service].append(ttfb)
            
            # Parse processing time
            service, proc_time = parse_processing_time(line)
            if service and proc_time:
                processing_metrics[service].append(proc_time)
            
            # Parse token usage
            prompt_tokens, completion_tokens = parse_tokens(line)
            if prompt_tokens and completion_tokens:
                token_usage.append({
                    'prompt': prompt_tokens,
                    'completion': completion_tokens,
                    'total': prompt_tokens + completion_tokens
                })
        
        if log_file != '-':
            lines.close()
    
    except FileNotFoundError:
        print(f"❌ Error: Log file '{log_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading log file: {e}")
        sys.exit(1)
    
    return ttfb_metrics, processing_metrics, token_usage


def print_summary(ttfb_metrics, processing_metrics, token_usage):
    """Print summary statistics."""
    print("\n" + "="*80)
    print("📊 PERFORMANCE METRICS SUMMARY")
    print("="*80 + "\n")
    
    # TTFB Summary
    if ttfb_metrics:
        print("⏱️  TIME TO FIRST BYTE (TTFB)\n")
        total_ttfb = 0
        for service, values in sorted(ttfb_metrics.items()):
            if not values:
                continue
            avg = mean(values)
            med = median(values)
            min_val = min(values)
            max_val = max(values)
            std = stdev(values) if len(values) > 1 else 0
            
            print(f"  {service}:")
            print(f"    Count:   {len(values)} requests")
            print(f"    Average: {avg:.2f}ms")
            print(f"    Median:  {med:.2f}ms")
            print(f"    Min:     {min_val:.2f}ms")
            print(f"    Max:     {max_val:.2f}ms")
            print(f"    StdDev:  {std:.2f}ms")
            
            # Add warning for slow services
            if avg > 3000:
                print(f"    ⚠️  WARNING: Average TTFB > 3000ms (bottleneck)")
            elif avg > 1500:
                print(f"    ⚠️  NOTICE: Average TTFB > 1500ms")
            
            total_ttfb += avg
            print()
        
        print(f"  📈 Total Pipeline TTFB: ~{total_ttfb:.2f}ms\n")
        
        if total_ttfb > 4000:
            print("  🔴 POOR: Total latency > 4 seconds")
        elif total_ttfb > 3000:
            print("  ⚠️  ACCEPTABLE: Total latency 3-4 seconds")
        elif total_ttfb > 2000:
            print("  ⚡ GOOD: Total latency 2-3 seconds")
        else:
            print("  ✅ EXCELLENT: Total latency < 2 seconds")
        print()
    
    # Token Usage Summary
    if token_usage:
        print("-"*80)
        print("\n💰 TOKEN USAGE\n")
        
        avg_prompt = mean([t['prompt'] for t in token_usage])
        avg_completion = mean([t['completion'] for t in token_usage])
        avg_total = mean([t['total'] for t in token_usage])
        
        print(f"  Requests analyzed: {len(token_usage)}")
        print(f"  Average prompt tokens:     {avg_prompt:.0f}")
        print(f"  Average completion tokens: {avg_completion:.0f}")
        print(f"  Average total tokens:      {avg_total:.0f}")
        
        if avg_prompt > 1500:
            print(f"  ⚠️  NOTICE: High prompt token count (consider shortening system prompt)")
        print()
    
    # Recommendations
    print("-"*80)
    print("\n🎯 OPTIMIZATION RECOMMENDATIONS\n")
    
    recommendations = []
    
    # Check LLM performance
    if 'AzureLLMService' in ttfb_metrics:
        llm_avg = mean(ttfb_metrics['AzureLLMService'])
        if llm_avg > 3000:
            recommendations.append({
                'priority': 'HIGH',
                'service': 'LLM',
                'issue': f'Average TTFB {llm_avg:.0f}ms (>3000ms)',
                'action': 'Switch to gpt-4o-mini or gpt-3.5-turbo for 2-3x speed improvement'
            })
        if token_usage and mean([t['prompt'] for t in token_usage]) > 1500:
            recommendations.append({
                'priority': 'MEDIUM',
                'service': 'LLM',
                'issue': f'Large prompt size (~{mean([t["prompt"] for t in token_usage]):.0f} tokens)',
                'action': 'Create a condensed version of your system prompt'
            })
    
    # Check TTS performance
    if 'ElevenLabsTTSService' in ttfb_metrics:
        tts_avg = mean(ttfb_metrics['ElevenLabsTTSService'])
        if tts_avg > 1000:
            recommendations.append({
                'priority': 'MEDIUM',
                'service': 'TTS',
                'issue': f'Average TTFB {tts_avg:.0f}ms (>1000ms)',
                'action': 'Use ElevenLabs Turbo v2.5 model for faster synthesis'
            })
    
    # Print recommendations
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            priority_emoji = '🔴' if rec['priority'] == 'HIGH' else '🟡'
            print(f"  {i}. {priority_emoji} [{rec['priority']}] {rec['service']}")
            print(f"     Issue:  {rec['issue']}")
            print(f"     Action: {rec['action']}")
            print()
    else:
        print("  ✅ Performance looks good! No major optimizations needed.\n")
    
    print("="*80 + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_metrics.py <log_file>")
        print("       python analyze_metrics.py -   (read from stdin)")
        sys.exit(1)
    
    log_file = sys.argv[1]
    
    print("📖 Analyzing logs...")
    ttfb_metrics, processing_metrics, token_usage = analyze_logs(log_file)
    
    if not ttfb_metrics and not token_usage:
        print("❌ No metrics found in log file.")
        print("   Make sure you're analyzing logs from a running bot with metrics enabled.")
        sys.exit(1)
    
    print_summary(ttfb_metrics, processing_metrics, token_usage)


if __name__ == "__main__":
    main()
