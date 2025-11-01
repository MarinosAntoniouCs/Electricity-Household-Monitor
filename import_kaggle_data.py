import csv
from measurements.models import Measurement
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Avg, Min, Max
import sys


def import_csv_data(csv_file_path):
    """
    Import electricity usage data from Kaggle CSV file with enhanced metrics calculation
    """
    
    print(f"Starting enhanced import from: {csv_file_path}")
    
    created_count = 0
    updated_count = 0
    error_count = 0
    
    try:
        with open(csv_file_path, 'r') as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    date_str = row['DATE'].strip()
                    start_time_str = row['START TIME'].strip()
                    end_time_str = row['END TIME'].strip()
                    
                    # Parse date
                    date_obj = None
                    for date_format in ['%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y']:
                        try:
                            date_obj = datetime.strptime(date_str, date_format).date()
                            break
                        except ValueError:
                            continue
                    
                    if not date_obj:
                        raise ValueError(f"Could not parse date: {date_str}")
                    
                    # Parse start time
                    start_time_obj = None
                    for time_format in ['%I:%M %p', '%H:%M', '%I:%M:%S %p', '%H:%M:%S']:
                        try:
                            start_time_obj = datetime.strptime(start_time_str, time_format).time()
                            break
                        except ValueError:
                            continue
                    
                    if not start_time_obj:
                        raise ValueError(f"Could not parse start time: {start_time_str}")
                    
                    # Parse end time
                    end_time_obj = None
                    for time_format in ['%I:%M %p', '%H:%M', '%I:%M:%S %p', '%H:%M:%S']:
                        try:
                            end_time_obj = datetime.strptime(end_time_str, time_format).time()
                            break
                        except ValueError:
                            continue
                    
                    if not end_time_obj:
                        raise ValueError(f"Could not parse end time: {end_time_str}")
                    
                    # Combine date and times
                    start_timestamp = datetime.combine(date_obj, start_time_obj)
                    end_timestamp = datetime.combine(date_obj, end_time_obj)
                    
                    # Handle case where end time is past midnight
                    if end_timestamp < start_timestamp:
                        end_timestamp += timedelta(days=1)
                    
                    # Calculate duration in minutes
                    duration_minutes = int((end_timestamp - start_timestamp).total_seconds() / 60)
                    
                    # Get consumption and cost
                    usage = row['USAGE'].strip()
                    consumption_kwh = Decimal(usage) if usage else Decimal('0')
                    
                    cost_str = row['COST'].strip().replace('$', '').replace(',', '')
                    cost = Decimal(cost_str) if cost_str else None
                    
                    # Calculate derived metrics
                    # 1. Average Power (kW) = Energy (kWh) / Time (hours)
                    if duration_minutes > 0:
                        duration_hours = Decimal(duration_minutes) / Decimal('60')
                        average_power_kw = consumption_kwh / duration_hours
                    else:
                        average_power_kw = None
                    
                    # 2. Cost per kWh
                    if cost and consumption_kwh > 0:
                        cost_per_kwh = cost / consumption_kwh
                    else:
                        cost_per_kwh = None
                    
                    # Create or update measurement
                    measurement, created = Measurement.objects.update_or_create(
                        meter_id='APARTMENT_METER',
                        timestamp=start_timestamp,
                        defaults={
                            'end_timestamp': end_timestamp,
                            'consumption_kwh': consumption_kwh,
                            'cost': cost,
                            'duration_minutes': duration_minutes,
                            'average_power_kw': average_power_kw,
                            'cost_per_kwh': cost_per_kwh,
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                    
                    if (created_count + updated_count) % 100 == 0:
                        print(f"Processed {created_count + updated_count} rows...")
                
                except Exception as e:
                    error_count += 1
                    print(f"Error on row {row_num}: {e}")
                    if error_count > 10:
                        print("Too many errors, stopping import.")
                        break
    
    except FileNotFoundError:
        print(f"Error: File not found: {csv_file_path}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    print("\n" + "="*50)
    print("Enhanced Import Complete!")
    print("="*50)
    print(f"✅ Created: {created_count}")
    print(f"🔄 Updated: {updated_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📊 Total processed: {created_count + updated_count}")
    print("="*50)
    
    # Calculate and display metrics summary
    if created_count + updated_count > 0:
        stats = Measurement.objects.aggregate(
            avg_duration=Avg('duration_minutes'),
            avg_power=Avg('average_power_kw'),
            avg_rate=Avg('cost_per_kwh'),
            min_rate=Min('cost_per_kwh'),
            max_rate=Max('cost_per_kwh')
        )
        
        print("\n📈 Calculated Metrics Summary:")
        if stats['avg_duration']:
            print(f"   Average Duration: {stats['avg_duration']:.1f} minutes")
        if stats['avg_power']:
            print(f"   Average Power: {stats['avg_power']:.3f} kW")
        if stats['avg_rate']:
            print(f"   Average Rate: ${stats['avg_rate']:.4f}/kWh")
        if stats['min_rate'] and stats['max_rate']:
            print(f"   Rate Range: ${stats['min_rate']:.4f} - ${stats['max_rate']:.4f}/kWh")
        print("="*50)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_kaggle_data.py /path/to/data.csv")
    else:
        import_csv_data(sys.argv[1])