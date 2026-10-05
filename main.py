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
		elif type(user_report) == dict:
			print(f"\n[+] {user_report.get("report_type")} report received. Sending to AI layer for processing...")
			# AI powered feature extraction
			user_input_extracted = ai_manager.extract_features(user_report)
			# print(user_input_extracted)

			if user_input_extracted is None:
				continue

			user_input_extracted = json.loads(user_input_extracted)
			# Found reports workflow: Extract features and store into database
			if user_report.get("report_type") == "found":
				# Store report into database
				print("[+] Storing found report into database...")
				try:
					data_manager.save_reports(user_input_extracted)
				except Exception as e:
					print(f"[!] Error saving report: {e}")
					continue
				print("\n" + "=" * 50)
				print("Found report stored successfully into database!")
				print("=" * 50)
			
			# Lost reports workflow: Extract features, perform semantic matching, pass to logic manager and output to user
			elif user_report.get("report_type") == "lost":
				# AI powered semantic matching
				print("\n" + "=" * 70)
				print("Attempting AI semantic matching with found reports in the database")
				print("=" * 70)
				print("[+] Pulling found reports from database for AI semantic matching...")
	
				# Pull found records from same category as the lost report from database
				report_category_list = data_manager.get_reports_by_category(user_input_extracted.get("category"))
				if not report_category_list:
					print(f"[!] No found reports reported for category: {user_input_extracted.get('category')}.")
					continue
				print(f"[+] Found {len(report_category_list)} found reports for category: {user_input_extracted.get('category')}.")
				matching_lost_reports = ai_manager.ai_semantic_matching(user_input_extracted, report_category_list) 
				print(matching_lost_reports)

				if not matching_lost_reports:
					continue

				# Business logic layer to apply multi rule conditions and output the best match to the user
				print("\n" + "=" * 75)
				print("Applying business logic to determine the best match for the lost report")
				print("=" * 75)
				best_match = logic_manager.get_best_match(json.loads(matching_lost_reports), json.loads(user_input_extracted).get("date"))
				print(best_match)

	return

if __name__=="__main__":
	main()
