import requests
import json
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ============ UPDATE THESE WITH YOUR APEX URLs ============
# Example: https://oracleapex.com/ords/social
BASE_URL = "https://oracleapex.com/ords/abidmasif/social/"

POSTS_URL = f"{BASE_URL}/posts/"
COMMENTS_URL = f"{BASE_URL}/comments/"
REACTIONS_URL = f"{BASE_URL}/reactions/"
USERS_URL = f"{BASE_URL}/users/"

# Browser-like headers (required)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def fetch_data(url):
    """Fetch data from REST endpoint"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30, verify=False)
        if response.status_code == 200:
            data = response.json()
            # Handle both direct array and wrapped response
            if isinstance(data, dict) and 'items' in data:
                return data['items']
            elif isinstance(data, dict) and 'results' in data:
                return data['results']
            elif isinstance(data, list):
                return data
            else:
                return []
        else:
            print(f"Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Connection error: {e}")
        return []

def get_top_posters(limit=5):
    """Calculate which users have posted the most"""
    posts = fetch_data(POSTS_URL)
    user_posts = {}
    
    for post in posts:
        user_id = post['user_id']
        user_posts[user_id] = user_posts.get(user_id, 0) + 1
    
    sorted_users = sorted(user_posts.items(), key=lambda x: x[1], reverse=True)
    return sorted_users[:limit]

def get_trending_posts(limit=5):
    """Get most liked posts"""
    posts = fetch_data(POSTS_URL)
    reactions = fetch_data(REACTIONS_URL)
    
    # Count likes per post
    post_likes = {post['post_id']: 0 for post in posts}
    
    for reaction in reactions:
        if reaction['post_id'] in post_likes:
            post_likes[reaction['post_id']] += 1
    
    # Return top posts with their like counts
    sorted_posts = sorted(post_likes.items(), key=lambda x: x[1], reverse=True)
    return sorted_posts[:limit]

def flag_inappropriate_content():
    """Find posts with banned words"""
    banned_words = ['spam', 'hate', 'inappropriate', 'ugly']
    posts = fetch_data(POSTS_URL)
    flagged = []
    
    for post in posts:
        text = post['text'].lower()
        for word in banned_words:
            if word in text:
                flagged.append({
                    'post_id': post['post_id'],
                    'text': post['text'],
                    'reason': f"Contains '{word}'"
                })
                break
    
    return flagged

def get_comment_stats():
    """How many comments per post"""
    comments = fetch_data(COMMENTS_URL)
    posts = fetch_data(POSTS_URL)
    
    comment_count = {}
    for post in posts:
        comment_count[post['post_id']] = 0
    
    for comment in comments:
        post_id = comment['post_id']
        if post_id in comment_count:
            comment_count[post_id] += 1
    
    return comment_count

def print_analytics():
    """Print full analytics dashboard"""
    print("\n" + "="*50)
    print("SOCIAL MEDIA ANALYTICS DASHBOARD")
    print("="*50 + "\n")
    
    # Top Posters
    print("📊 TOP POSTERS (by number of posts):")
    print("-" * 50)
    top_posters = get_top_posters()
    for rank, (user_id, count) in enumerate(top_posters, 1):
        print(f"  #{rank} User {user_id}: {count} posts")
    
    # Trending Posts
    print("\n🔥 TRENDING POSTS (by likes):")
    print("-" * 50)
    trending = get_trending_posts()
    for rank, (post_id, likes) in enumerate(trending, 1):
        print(f"  #{rank} Post {post_id}: {likes} likes")
    
    # Comment Stats
    print("\n💬 COMMENT ACTIVITY:")
    print("-" * 50)
    comments = get_comment_stats()
    total_comments = sum(comments.values())
    avg_comments = total_comments / len(comments) if comments else 0
    print(f"  Total comments: {total_comments}")
    print(f"  Average comments per post: {avg_comments:.1f}")
    
    # Flagged Content
    print("\n⚠️  FLAGGED CONTENT (inappropriate):")
    print("-" * 50)
    flagged = flag_inappropriate_content()
    if flagged:
        for item in flagged:
            print(f"  Post {item['post_id']}: {item['reason']}")
            print(f"    Text: {item['text'][:50]}...")
    else:
        print("  None found ✓")
    
    print("\n" + "="*50)
    print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50 + "\n")

if __name__ == "__main__":
    print_analytics()