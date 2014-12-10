import urllib2
import json
import datetime

def create_post_url(graph_url, APP_ID, APP_SECRET):
	#method to return 
	post_args = "/posts/?key=value&access_token=" + APP_ID + "|" + APP_SECRET
	post_url = graph_url + post_args
	return post_url
	
# ========================================================================================
	
def render_to_json(graph_url):
	#render graph url call to JSON
	web_response = urllib2.urlopen(graph_url)
	readable_page = web_response.read()
	json_data = json.loads(readable_page)
	return json_data
	
# ========================================================================================

def scrape_posts_by_date(graph_url, date, post_data, APP_ID, APP_SECRET):
	#render URL to JSON
	page_posts = render_to_json(graph_url)
	
	#extract next page
	next_page = page_posts["paging"]["next"]
	
	#grab all posts
	page_posts = page_posts["data"]
	
	#boolean to tell us when to stop collecting
	collecting = True
	
	#for each post capture data
	for post in page_posts:
		try:
			likes_count = get_likes_count(post["id"], APP_ID, APP_SECRET)
			current_post = [post["id"], post["message"],
					post["created_time"],
                                        post["shares"]["count"]]		
							
		except Exception:
			current_post = [ "error", "error", "error", "error"]
			
		if current_post[2] != "error":
                #compare dates
			if date <= current_post[2]:
				post_data.append(current_post)
			
			elif date > current_post[2]:
				print "Done collecting"
				collecting = False
				break
	
	
	#If we still don't meet date requirements, run on next page			
	if collecting == True:
		scrape_posts_by_date(next_page, date, post_data, '---------------', '---------------------------------')
	
	return post_data

# ========================================================================================

def get_likes_count(post_id, APP_ID, APP_SECRET):
	#create Graph API Call
	graph_url = "https://graph.facebook.com/" 
	likes_args = post_id + "/likes?summary=true&key=value&access_token" + APP_ID + "|" + APP_SECRET
	likes_url = graph_url + likes_args
	likes_json = render_to_json(likes_url)

	#pick out the likes count
	count_likes = likes_json["summary"]["total_count"]

	return count_likes
	
# ========================================================================================

def create_comments_url(graph_url, post_id, APP_ID, APP_SECRET):
	#create Graph API Call
	comments_args = post_id + "/comments/?key=value&access_token=" + APP_ID + "|" + APP_SECRET
	comments_url = graph_url + comments_args
	
	return comments_url
	
# ========================================================================================

def get_comments_data(comments_url, comment_data, post_id):
	#render URL to JSON
	comments = render_to_json(comments_url)["data"]
	
	#for each comment capture data
	for comment in comments:
		try:
			current_comments = [comment["id"], comment["message"], comment["like_count"],
					    comment["created_time"], post_id]
			
			comment_data.append(current_comments)
			
		except Exception:
			current_comments = ["error", "error", "error", "error", "error"]
			
			
	#check if there is another page
	try:
		#extract next page
		next_page = comments["paging"]["next"]
	except Exception:
		next_page = None
			
			
	#if we have another page, recurse
	if next_page is not None:
		get_comments_data(next_page, comment_data, post_id)
	else:
		return comment_data
		
# ========================================================================================
		
def main():
	#to find username go to  FB page, copy the end of URL 
	#e.g. http://facebook.com/Symantec, Symantec is the username
	list_companies = ["Symantec"]
	graph_url = "https://graph.facebook.com/"
	
	#the time of last weeks crawl
	last_crawl = datetime.datetime.now() - datetime.timedelta(weeks=2)
	last_crawl = last_crawl.isoformat()
	
	for company in list_companies:
		#make graph api url with company username
		current_page = graph_url + company
		
		#open public page in facebook graph api
		json_fbpage = render_to_json(current_page)

		#print page data to console
		print company + " page"
		page_data = [json_fbpage["id"], 
						json_fbpage["likes"], 
						json_fbpage["talking_about_count"],
						json_fbpage["link"], 
						json_fbpage["username"], 
						json_fbpage["website"]]
						
		print page_data
		print "            "
		
		#extract post data
		post_url = create_post_url(current_page, '---------------', '---------------------------------')

		post_data = []
		post_data = scrape_posts_by_date(post_url, last_crawl, post_data, '---------------', '---------------------------------')

		print post_data
		
		#extract likes count on posts
		likes_count = get_likes_count('8988037875_10152462707092876', '---------------', '---------------------------------')
		
		print likes_count
		
		#extract comments of posts
		comments_url = create_comments_url(current_page, '---------------', '---------------------------------')
		
		comment_data = []
		comment_data = get_comments_data(comments_url, comment_data, '8988037875_10152462707092876')
		

if __name__ == "__main__":
	main()   