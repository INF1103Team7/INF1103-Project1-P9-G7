import io_manager
import ai_manager
import data_manager
import logic_manager
import json

def main():
	while True:
		# Run the CLI interface for the AI powered lost and found system
		user_report = io_manager.run_cli()
		
		if user_report == "quit":
			break

		# AI layer to process report types
		elif type(user_report) == dict and user_report.get("report_type") == "found":
			print("\n[+] Found report received. Sending to AI layer for processing...")
			# AI powered feature extraction
			user_input_extracted = ai_manager.extract_features(user_report)
			# print(user_input_extracted)

			if user_input_extracted is None:
				continue

			# Store report into database
			print("[+] Storing found report into database...")
			try:
				data_manager.save_reports(json.loads(user_input_extracted))
			except Exception as e:
				print(f"[!] Error saving report: {e}")
				continue
			print("[+] Found report stored successfully into database.")

		elif type(user_report) == dict and user_report.get("report_type") == "lost":
			print("\n[+] Lost report received. Sending to AI layer for processing...")
			# AI powered feature extraction
			user_input_extracted = ai_manager.extract_features(user_report)
			# print(user_input_extracted)

			if user_input_extracted is None:
				continue

			# # AI powered semantic matching
			# # Pull found records from same category as the lost report from database
			print("[+] Pulling found reports from database for AI semantic matching...")
			# # report_category_list = "Pull from database"
			# matching_lost_reports = ai_manager.ai_semantic_matching(user_input_extracted) 
			# print(matching_lost_reports)

	return

if __name__=="__main__":
	main()
